"""
generate_data.py
================
Master data generation script for the Fabric IQ Education Demo.
Context: Singapore university (NUS-style grading, SGD, Aug-start academic year).

Generates all 13 tables in strict FK-dependency order:
  1. dim_date               7. dim_exam_type
  2. dim_department         8. dim_fee_type
  3. dim_program            9. dim_academic_period
  4. dim_staff             10. dim_student
  5. dim_course            11. fact_enrollments
  6. bridge_course_program 12. fact_exam_results
                           13. fact_financial_transactions

Usage (local):
  pip install -r requirements.txt
  python scripts/generate_data.py --format both --output-dir data
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from faker import Faker
from scipy.stats import truncnorm

# ── So the script can be run from the project root or scripts/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CONFIG, DEPARTMENTS, EXAM_TYPES, FEE_TYPES, PROGRAMS  # noqa: E402

# ── Reproducibility ───────────────────────────────────────────────────────────
SEED = CONFIG["seed"]
random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)
fake = Faker(CONFIG["faker_locale"])

# ── Helpers ───────────────────────────────────────────────────────────────────


def date_to_key(d: date) -> int:
    """Convert a date to an integer YYYYMMDD key."""
    return int(d.strftime("%Y%m%d"))


def random_date(start: date, end: date) -> date:
    """Return a random date between start and end (inclusive)."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def bimodal_score(is_fail: bool, international: bool, repeat: bool) -> float:
    """
    Draw a score from the appropriate truncated normal distribution.
    Returns a float in [0, 100].
    """
    if is_fail:
        mean = CONFIG["score_fail_mean"]
        std = CONFIG["score_fail_std"]
        lo, hi = CONFIG["score_fail_min"], CONFIG["score_fail_max"]
    else:
        mean = CONFIG["score_pass_mean"]
        std = CONFIG["score_pass_std"]
        lo, hi = CONFIG["score_pass_min"], CONFIG["score_pass_max"]

    if international:
        mean -= CONFIG["international_penalty"]
    if repeat:
        mean += CONFIG["repeat_bonus"]

    mean = max(lo + 1, min(hi - 1, mean))
    a = (lo - mean) / std
    b = (hi - mean) / std
    score = truncnorm.rvs(a, b, loc=mean, scale=std)
    return round(float(np.clip(score, lo, hi)), 2)


def score_to_grade(pct: float) -> tuple[str, float]:
    """Return (grade_letter, grade_points) for a given percentage score."""
    for boundary in CONFIG["grade_boundaries"]:
        if boundary["min"] <= pct <= boundary["max"]:
            return boundary["letter"], boundary["points"]
    return "F", 0.0


# ── Generator 1: dim_date ──────────────────────────────────────────────────────

def generate_dim_date() -> pd.DataFrame:
    print("Generating dim_date ...")
    start = date.fromisoformat(CONFIG["date_dim_start"])
    end = date.fromisoformat(CONFIG["date_dim_end"])

    # Build exam-period lookup (list of (start, end) tuples)
    exam_periods: list[tuple[date, date]] = []
    for year in range(start.year, end.year + 1):
        for mmdd_start, mmdd_end in [
            (CONFIG["semester1_exam_start_mmdd"], CONFIG["semester1_exam_end_mmdd"]),
            (CONFIG["semester2_exam_start_mmdd"], CONFIG["semester2_exam_end_mmdd"]),
        ]:
            try:
                ep_start = date(year, mmdd_start[0], mmdd_start[1])
                ep_end = date(year, mmdd_end[0], mmdd_end[1])
                exam_periods.append((ep_start, ep_end))
            except ValueError:
                pass

    month_shorts = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    rows: list[dict] = []
    current = start
    while current <= end:
        is_exam = any(ep[0] <= current <= ep[1] for ep in exam_periods)
        # Singapore academic year: Aug–Jul. Aug of that year = start of academic year.
        acad_year = current.year if current.month >= 8 else current.year - 1

        rows.append({
            "date_key": date_to_key(current),
            "full_date": current,
            "day_of_week": current.strftime("%A"),
            "day_number_in_week": current.isoweekday(),   # 1=Monday, 7=Sunday
            "day_number_in_month": current.day,
            "day_number_in_year": current.timetuple().tm_yday,
            "week_number_in_year": int(current.strftime("%W")),
            "month_number": current.month,
            "month_name": month_names[current.month - 1],
            "month_short": month_shorts[current.month - 1],
            "quarter_number": (current.month - 1) // 3 + 1,
            "quarter_label": f"Q{(current.month - 1) // 3 + 1} {current.year}",
            "year": current.year,
            "academic_year": acad_year,
            "is_weekday": current.isoweekday() <= 5,
            "is_public_holiday": False,
            "is_exam_period": is_exam,
        })
        current += timedelta(days=1)

    df = pd.DataFrame(rows)
    print(f"  dim_date: {len(df):,} rows")
    return df


# ── Generator 2: dim_department ───────────────────────────────────────────────

def generate_dim_department() -> pd.DataFrame:
    print("Generating dim_department ...")
    rows = []
    for key, dept in enumerate(DEPARTMENTS, start=1):
        rows.append({
            "department_key": key,
            "department_id": dept["id"],
            "department_name": dept["name"],
            "faculty": dept["faculty"],
            "head_of_department": fake.name(),
            "phone": fake.phone_number(),
            "email": f"{dept['id'].lower().replace('-', '.')}@university.edu.sg",
            "location_building": f"Building {random.randint(1, 20):02d}",
            "budget_code": f"BC-{random.randint(1000, 9999)}",
            "is_active": True,
        })
    df = pd.DataFrame(rows)
    print(f"  dim_department: {len(df):,} rows")
    return df


# ── Generator 3: dim_program ──────────────────────────────────────────────────

def generate_dim_program(df_dept: pd.DataFrame) -> pd.DataFrame:
    print("Generating dim_program ...")
    dept_id_to_key = dict(zip(df_dept["department_id"], df_dept["department_key"]))
    rows = []
    for key, prog in enumerate(PROGRAMS, start=1):
        dept_key = dept_id_to_key[prog["dept_id"]]
        faculty = df_dept.loc[df_dept["department_key"] == dept_key, "faculty"].values[0]
        total_cp = int(round(prog["years"])) * 40  # 40 modular credits per year (5 modules × 4MC × 2 sem)
        domestic_fee = CONFIG["domestic_fee_per_credit_point"] * total_cp
        intl_fee = domestic_fee * CONFIG["international_multiplier"]
        rows.append({
            "program_key": key,
            "program_id": prog["id"],
            "program_name": prog["name"],
            "program_type": prog["type"],
            "duration_years": prog["years"],
            "total_credit_points": total_cp,
            "department_key": dept_key,
            "faculty": faculty,
            "igp_score": prog["igp_score"],
            "annual_domestic_fee": round(domestic_fee / prog["years"], 2),
            "annual_international_fee": round(intl_fee / prog["years"], 2),
            "delivery_mode": random.choice(["On-campus", "Hybrid", "On-campus", "On-campus"]),
            "accreditation_body": "MOE Singapore" if prog["type"] == "Bachelor" else None,
            "is_active": True,
        })
    df = pd.DataFrame(rows)
    print(f"  dim_program: {len(df):,} rows")
    return df


# ── Generator 4: dim_staff ────────────────────────────────────────────────────

ROLE_TITLES = [
    ("Professor", "Academic"),
    ("Associate Professor", "Academic"),
    ("Senior Lecturer", "Academic"),
    ("Lecturer", "Academic"),
    ("Tutor", "Academic"),
    ("Research Fellow", "Research"),
    ("Sessional Lecturer", "Academic"),
    ("Course Coordinator", "Academic"),
    ("Department Manager", "Administrative"),
    ("Administrative Officer", "Administrative"),
    ("Academic Advisor", "Administrative"),
    ("IT Support Officer", "Administrative"),
]


def generate_dim_staff(df_dept: pd.DataFrame) -> pd.DataFrame:
    print("Generating dim_staff ...")
    dept_keys = df_dept["department_key"].tolist()
    rows = []
    for i in range(1, CONFIG["n_staff"] + 1):
        role_title, role_category = random.choice(ROLE_TITLES)
        dept_key = random.choice(dept_keys)
        join_date = random_date(date(2010, 1, 1), date(2023, 12, 31))
        rows.append({
            "staff_key": i,
            "staff_id": f"STAFF-{i:04d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": f"staff{i:04d}@university.edu.sg",
            "role_title": role_title,
            "role_category": role_category,
            "department_key": dept_key,
            "employment_type": random.choices(
                ["Full-time", "Part-time", "Casual"], weights=[0.6, 0.25, 0.15]
            )[0],
            "date_joined": join_date,
            "salary_band": random.choice(["Band A", "Band B", "Band C", "Band D", "Band E", "Band F"]),
            "is_active": random.random() > 0.05,
        })
    df = pd.DataFrame(rows)
    print(f"  dim_staff: {len(df):,} rows")
    return df


# ── Generator 5: dim_course ───────────────────────────────────────────────────

COURSE_PREFIXES = {
    "DEPT-CS":  ("COMP", ["Programming", "Data Structures", "Algorithms", "Databases",
                           "Networks", "Software Engineering", "Machine Learning",
                           "Cybersecurity", "Cloud Computing", "Web Development",
                           "Operating Systems", "Artificial Intelligence"]),
    "DEPT-ENG": ("ELEC", ["Circuit Theory", "Digital Systems", "Signal Processing",
                           "Power Systems", "Embedded Systems", "Control Theory",
                           "Telecommunications", "Electromagnetics"]),
    "DEPT-BUS": ("BUAD", ["Management", "Marketing", "Organisational Behaviour",
                           "Strategic Management", "Operations Management",
                           "Business Communication", "Entrepreneurship",
                           "Supply Chain Management"]),
    "DEPT-ACC": ("ACCT", ["Financial Accounting", "Management Accounting",
                           "Auditing", "Taxation", "Corporate Finance",
                           "Financial Management", "Cost Accounting"]),
    "DEPT-NUR": ("NURS", ["Anatomy", "Nursing Practice", "Clinical Skills",
                           "Pharmacology", "Mental Health Nursing",
                           "Community Health", "Palliative Care"]),
    "DEPT-MED": ("MEDC", ["Medical Biochemistry", "Pathology", "Physiology",
                           "Microbiology", "Immunology", "Genetics", "Cell Biology"]),
    "DEPT-EDU": ("EDUC", ["Curriculum Design", "Educational Psychology",
                           "Classroom Management", "Inclusive Education",
                           "Assessment Methods", "Early Childhood Education"]),
    "DEPT-LAW": ("LAWS", ["Contract Law", "Tort Law", "Constitutional Law",
                           "Criminal Law", "Property Law", "Administrative Law",
                           "International Law", "Legal Research"]),
}

COURSE_LEVELS = {
    "Bachelor": "Undergraduate",
    "Master": "Postgraduate",
    "Diploma": "Postgraduate",
}


def generate_dim_course(df_dept: pd.DataFrame, df_staff: pd.DataFrame) -> pd.DataFrame:
    print("Generating dim_course ...")
    dept_id_to_key = dict(zip(df_dept["department_id"], df_dept["department_key"]))
    # Academic staff only as coordinators
    academic_staff = df_staff[df_staff["role_category"] == "Academic"]["staff_key"].tolist()

    n_per_dept = CONFIG["n_courses"] // len(DEPARTMENTS)
    remainder = CONFIG["n_courses"] % len(DEPARTMENTS)
    rows = []
    course_key = 1

    for dept_idx, (dept_id, (prefix, topics)) in enumerate(COURSE_PREFIXES.items()):
        dept_key = dept_id_to_key[dept_id]
        n = n_per_dept + (1 if dept_idx < remainder else 0)
        level_num = 1000
        for i in range(n):
            topic = topics[i % len(topics)]
            rows.append({
                "course_key": course_key,
                "course_id": f"{prefix}{level_num + i * 100:04d}",
                "course_name": topic,
                "credit_points": 4,
                "level": "Undergraduate" if level_num + i * 100 < 5000 else "Postgraduate",
                "department_key": dept_key,
                "coordinator_staff_key": random.choice(academic_staff),
                "prerequisite_course_id": None,  # simplified for demo
                "delivery_mode": random.choices(
                    ["On-campus", "Online", "Hybrid"], weights=[0.6, 0.2, 0.2]
                )[0],
                "is_core": random.random() > 0.25,
                "is_active": True,
                "description": f"An introduction to {topic.lower()} concepts and applications.",
            })
            course_key += 1

    df = pd.DataFrame(rows)
    print(f"  dim_course: {len(df):,} rows")
    return df


# ── Generator 6: bridge_course_program ───────────────────────────────────────

def generate_bridge_course_program(
    df_course: pd.DataFrame, df_program: pd.DataFrame, df_dept: pd.DataFrame
) -> pd.DataFrame:
    print("Generating bridge_course_program ...")
    dept_id_to_key = dict(zip(df_dept["department_id"], df_dept["department_key"]))

    rows = []
    for _, prog in df_program.iterrows():
        prog_dept_key = prog["department_key"]
        prog_years = int(round(prog["duration_years"]))
        # Assign courses from same department (core) + some cross-department (electives)
        same_dept_courses = df_course[df_course["department_key"] == prog_dept_key]["course_key"].tolist()
        other_courses = df_course[df_course["department_key"] != prog_dept_key]["course_key"].tolist()

        # Aim for 5 modules × 2 semesters × n years = 10*n courses total
        total_slots = 10 * prog_years
        n_core = min(len(same_dept_courses), int(total_slots * 0.7))
        n_elective = min(len(other_courses), total_slots - n_core)

        core_courses = random.sample(same_dept_courses, n_core)
        elective_courses = random.sample(other_courses, n_elective)

        seq = 1
        for ck in core_courses:
            year = ((seq - 1) // (total_slots // prog_years)) + 1
            rows.append({
                "course_key": ck,
                "program_key": int(prog["program_key"]),
                "course_sequence": seq,
                "is_core": True,
                "year_of_program": min(year, prog_years),
            })
            seq += 1

        for ck in elective_courses:
            year = ((seq - 1) // (total_slots // prog_years)) + 1
            rows.append({
                "course_key": ck,
                "program_key": int(prog["program_key"]),
                "course_sequence": seq,
                "is_core": False,
                "year_of_program": min(year, prog_years),
            })
            seq += 1

    df = pd.DataFrame(rows).drop_duplicates(subset=["course_key", "program_key"])
    print(f"  bridge_course_program: {len(df):,} rows")
    return df


# ── Generator 7: dim_exam_type ────────────────────────────────────────────────

def generate_dim_exam_type() -> pd.DataFrame:
    print("Generating dim_exam_type ...")
    rows = []
    for key, et in enumerate(EXAM_TYPES, start=1):
        rows.append({
            "exam_type_key": key,
            "exam_type_id": et["id"],
            "exam_type_name": et["name"],
            "category": et["category"],
            "weighting_typical_pct": et["weight"],
            "duration_minutes": et["duration"],
            "is_open_book": et["open_book"],
        })
    df = pd.DataFrame(rows)
    print(f"  dim_exam_type: {len(df):,} rows")
    return df


# ── Generator 8: dim_fee_type ─────────────────────────────────────────────────

def generate_dim_fee_type() -> pd.DataFrame:
    print("Generating dim_fee_type ...")
    rows = []
    for key, ft in enumerate(FEE_TYPES, start=1):
        rows.append({
            "fee_type_key": key,
            "fee_type_id": ft["id"],
            "fee_type_name": ft["name"],
            "fee_category": ft["category"],
            "is_mandatory": ft["mandatory"],
            "gst_applicable": ft["gst"],
        })
    df = pd.DataFrame(rows)
    print(f"  dim_fee_type: {len(df):,} rows")
    return df


# ── Generator 9: dim_academic_period ─────────────────────────────────────────

def generate_dim_academic_period() -> pd.DataFrame:
    print("Generating dim_academic_period ...")
    rows = []
    key = 1
    years = CONFIG["academic_years"]

    for year in years:
        for sem_idx, semester in enumerate(CONFIG["semesters_per_year"]):
            if semester == "Semester 1":
                s = date(year, CONFIG["semester1_start_mmdd"][0], CONFIG["semester1_start_mmdd"][1])
                e = date(year, CONFIG["semester1_end_mmdd"][0], CONFIG["semester1_end_mmdd"][1])
                census = date(year, CONFIG["semester1_census_mmdd"][0], CONFIG["semester1_census_mmdd"][1])
                ex_s = date(year, CONFIG["semester1_exam_start_mmdd"][0], CONFIG["semester1_exam_start_mmdd"][1])
                ex_e = date(year, CONFIG["semester1_exam_end_mmdd"][0], CONFIG["semester1_exam_end_mmdd"][1])
            else:
                s = date(year, CONFIG["semester2_start_mmdd"][0], CONFIG["semester2_start_mmdd"][1])
                e = date(year, CONFIG["semester2_end_mmdd"][0], CONFIG["semester2_end_mmdd"][1])
                census = date(year, CONFIG["semester2_census_mmdd"][0], CONFIG["semester2_census_mmdd"][1])
                ex_s = date(year, CONFIG["semester2_exam_start_mmdd"][0], CONFIG["semester2_exam_start_mmdd"][1])
                ex_e = date(year, CONFIG["semester2_exam_end_mmdd"][0], CONFIG["semester2_exam_end_mmdd"][1])

            rows.append({
                "academic_period_key": key,
                "period_id": f"{year}-S{sem_idx + 1}",
                "academic_year": year,
                "semester": semester,
                "period_label": f"{semester} {year}",
                "start_date": s,
                "end_date": e,
                "census_date": census,
                "exam_period_start": ex_s,
                "exam_period_end": ex_e,
                "is_current": (year == max(years) and semester == "Semester 2"),
            })
            key += 1

    df = pd.DataFrame(rows)
    print(f"  dim_academic_period: {len(df):,} rows")
    return df


# ── Generator 10: dim_student ─────────────────────────────────────────────────

COUNTRIES_INTERNATIONAL = [
    "China", "India", "Malaysia", "Indonesia", "Vietnam",
    "South Korea", "Myanmar", "Bangladesh", "Philippines", "Thailand",
    "Japan", "Taiwan", "Pakistan", "Sri Lanka", "Hong Kong",
]

SCHOLARSHIP_TYPES = [
    "ASEAN Scholarship",
    "Dean's List Award",
    "MOE Tuition Grant Scholar",
    "University Merit Scholarship",
    "Singapore Government Scholarship",
    None,
]


def generate_dim_student(df_program: pd.DataFrame, df_dept: pd.DataFrame) -> pd.DataFrame:
    print("Generating dim_student ...")
    n = CONFIG["n_students"]
    program_keys = df_program["program_key"].tolist()
    dept_keys = df_dept["department_key"].tolist()
    enrol_statuses = list(CONFIG["enrolment_status_weights"].keys())
    enrol_weights = list(CONFIG["enrolment_status_weights"].values())
    academic_years = CONFIG["academic_years"]

    rows = []
    for i in range(1, n + 1):
        domestic = random.random() < CONFIG["domestic_ratio"]
        country = "Singapore" if domestic else random.choice(COUNTRIES_INTERNATIONAL)
        nationality = "Singaporean" if domestic else country
        acad_year_start = random.choice(academic_years)
        # Start date: random day in August of the enrolment year (S1 starts Aug)
        enrol_date = random_date(date(acad_year_start, 8, 1), date(acad_year_start, 8, 20))
        prog_key = random.choice(program_keys)
        duration = df_program.loc[df_program["program_key"] == prog_key, "duration_years"].values[0]
        expected_grad = date(acad_year_start + int(round(duration)), 6, 30)
        status = random.choices(enrol_statuses, weights=enrol_weights)[0]
        # Over-represent Active for students who enrolled recently
        if acad_year_start == max(academic_years):
            status = random.choices(
                ["Active", "Withdrawn"], weights=[0.93, 0.07]
            )[0]

        scholarship = False
        scholarship_type = None
        if domestic and random.random() < CONFIG["scholarship_rate_domestic"]:
            scholarship = True
            scholarship_type = random.choice([t for t in SCHOLARSHIP_TYPES if t])

        rows.append({
            "student_key": i,
            "student_id": f"STU-{acad_year_start}-{i:04d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "date_of_birth": fake.date_of_birth(minimum_age=17, maximum_age=45),
            "gender": random.choices(
                ["Male", "Female", "Non-binary", "Prefer not to say"],
                weights=[0.48, 0.48, 0.03, 0.01]
            )[0],
            "email": f"stu{i:04d}@e.university.edu.sg",
            "phone": fake.phone_number(),
            "address_street": fake.street_address(),
            "address_suburb": fake.city(),
            "address_state": fake.state_abbr(),
            "address_postcode": fake.postcode(),
            "country_of_birth": country,
            "nationality": nationality,
            "domestic_international": "Domestic" if domestic else "International",
            "enrolment_status": status,
            "enrolment_date": enrol_date,
            "expected_graduation_date": expected_grad,
            "program_key": prog_key,
            "department_key": df_program.loc[
                df_program["program_key"] == prog_key, "department_key"
            ].values[0],
            "academic_year_start": acad_year_start,
            "scholarship_flag": scholarship,
            "scholarship_type": scholarship_type,
            "disability_support_flag": random.random() < 0.06,
            "first_in_family_flag": random.random() < 0.20,
            "permanent_resident_flag": random.random() < 0.20 if domestic else False,
        })

    df = pd.DataFrame(rows)
    print(f"  dim_student: {len(df):,} rows")
    return df


# ── Generator 11: fact_enrollments ───────────────────────────────────────────

ENROLLMENT_STATUSES = ["Enrolled", "Completed", "Failed", "Withdrawn", "Deferred"]


def generate_fact_enrollments(
    df_student: pd.DataFrame,
    df_course: pd.DataFrame,
    df_program: pd.DataFrame,
    df_academic_period: pd.DataFrame,
    df_bridge: pd.DataFrame,
    df_date: pd.DataFrame,
) -> pd.DataFrame:
    print("Generating fact_enrollments ...")
    date_keys = df_date["date_key"].tolist()

    # Build per-program course list from bridge
    prog_courses: dict[int, list[int]] = {}
    for _, row in df_bridge.iterrows():
        pk = int(row["program_key"])
        ck = int(row["course_key"])
        prog_courses.setdefault(pk, []).append(ck)

    rows = []
    enroll_key = 1

    for _, student in df_student.iterrows():
        student_key = int(student["student_key"])
        prog_key = int(student["program_key"])
        is_intl = student["domestic_international"] == "International"
        start_year = int(student["academic_year_start"])
        status = student["enrolment_status"]

        # Determine which periods this student is active across
        active_periods = df_academic_period[
            df_academic_period["academic_year"] >= start_year
        ]
        if status == "Withdrawn":
            # Only enrolled for 1-2 periods then withdrawn
            active_periods = active_periods.head(random.randint(1, 2))
        elif status == "Graduated":
            # Enrolled for the full duration of their program
            prog_duration = int(round(
                df_program.loc[df_program["program_key"] == prog_key, "duration_years"].values[0]
            ))
            max_year = start_year + prog_duration
            active_periods = active_periods[active_periods["academic_year"] <= max_year]
        # Active and Suspended students: enrol in all available periods

        available_courses = prog_courses.get(prog_key, df_course["course_key"].tolist()[:20])
        completed_course_keys: set[int] = set()

        for _, period in active_periods.iterrows():
            period_key = int(period["academic_period_key"])
            period_start: date = period["start_date"]
            period_census: date = period["census_date"]
            period_end: date = period["end_date"]

            # Pick courses for this semester (don't repeat completed courses)
            eligible = [ck for ck in available_courses if ck not in completed_course_keys]
            n_courses = min(
                len(eligible),
                random.randint(
                    CONFIG["avg_courses_per_student_per_semester"] - 1,
                    CONFIG["avg_courses_per_student_per_semester"] + 1,
                ),
            )
            if n_courses == 0:
                break

            semester_courses = random.sample(eligible, n_courses)
            for course_key in semester_courses:
                enroll_date = random_date(period_start, period_start + timedelta(days=10))
                is_withdrawn = random.random() < CONFIG["withdrawal_rate"]
                withdrew_before_census = False
                withdraw_date = None

                if is_withdrawn:
                    before_census = random.random() < 0.6
                    if before_census:
                        withdraw_date = random_date(enroll_date, period_census)
                        withdrew_before_census = True
                    else:
                        withdraw_date = random_date(period_census + timedelta(days=1), period_end)
                    enroll_status = "Withdrawn"
                    final_grade = None
                    gpa_points = None
                    cp_earned = 0
                elif status == "Deferred":
                    enroll_status = "Deferred"
                    final_grade = None
                    gpa_points = None
                    cp_earned = 0
                elif period["is_current"] and status == "Active":
                    # Active students in the current period are still enrolled
                    enroll_status = "Enrolled"
                    final_grade = None
                    gpa_points = None
                    cp_earned = 0
                else:
                    # Determine final grade from a placeholder score
                    # (actual grades live in fact_exam_results; this is the course aggregate)
                    is_fail = random.random() < CONFIG["fail_rate"]
                    score = bimodal_score(is_fail, is_intl, False)
                    final_grade, gpa_points = score_to_grade(score)
                    cp_earned = 4 if final_grade != "F" else 0
                    enroll_status = "Completed" if final_grade != "F" else "Failed"
                    completed_course_keys.add(course_key)

                enroll_dk = date_to_key(enroll_date)
                withdraw_dk = date_to_key(withdraw_date) if withdraw_date else None

                rows.append({
                    "enrollment_key": enroll_key,
                    "student_key": student_key,
                    "course_key": course_key,
                    "academic_period_key": period_key,
                    "program_key": prog_key,
                    "enroll_date_key": enroll_dk,
                    "withdraw_date_key": withdraw_dk,
                    "enrollment_status": enroll_status,
                    "enrollment_type": "Full-time",
                    "delivery_mode": random.choices(
                        ["On-campus", "Online", "Hybrid"], weights=[0.65, 0.20, 0.15]
                    )[0],
                    "course_final_grade_letter": final_grade,
                    "course_gpa_points": gpa_points,
                    "credit_points_attempted": 4,
                    "credit_points_earned": cp_earned,
                    "is_repeat": False,
                    "withdrew_before_census": withdrew_before_census,
                    "academic_load": 1.0,
                })
                enroll_key += 1

    df = pd.DataFrame(rows)
    print(f"  fact_enrollments: {len(df):,} rows")
    return df


# ── Generator 12: fact_exam_results ──────────────────────────────────────────

def generate_fact_exam_results(
    df_enrollments: pd.DataFrame,
    df_exam_type: pd.DataFrame,
    df_student: pd.DataFrame,
    df_academic_period: pd.DataFrame,
    df_staff: pd.DataFrame,
    df_date: pd.DataFrame,
) -> pd.DataFrame:
    print("Generating fact_exam_results ...")

    # Only generate results for completed/failed enrollments (not withdrawn, deferred, or still enrolled)
    active_enrollments = df_enrollments[
        ~df_enrollments["enrollment_status"].isin(["Withdrawn", "Deferred", "Enrolled"])
    ]

    student_intl: dict[int, bool] = dict(
        zip(
            df_student["student_key"],
            df_student["domestic_international"].map(lambda x: x == "International"),
        )
    )

    exam_type_list = df_exam_type.to_dict("records")
    academic_staff_keys = df_staff[df_staff["role_category"] == "Academic"]["staff_key"].tolist()

    period_exam_dates: dict[int, tuple[date, date]] = {}
    for _, p in df_academic_period.iterrows():
        period_exam_dates[int(p["academic_period_key"])] = (
            p["exam_period_start"],
            p["exam_period_end"],
        )

    rows = []
    result_key = 1

    for _, enroll in active_enrollments.iterrows():
        student_key = int(enroll["student_key"])
        course_key = int(enroll["course_key"])
        period_key = int(enroll["academic_period_key"])
        is_intl = student_intl.get(student_key, False)
        final_grade = enroll["course_final_grade_letter"]

        ex_start, ex_end = period_exam_dates[period_key]

        for et in exam_type_list:
            et_key = int(et["exam_type_key"])
            et_category = et["category"]
            weighting = et["weighting_typical_pct"]

            # Ensure score is consistent with the overall course grade
            if final_grade == "F":
                is_fail = random.random() < 0.5  # half the assessments they fail
            else:
                is_fail = random.random() < 0.04  # occasionally fail an individual assessment

            score_pct = bimodal_score(is_fail, is_intl, bool(enroll["is_repeat"]))
            grade_letter, grade_pts = score_to_grade(score_pct)

            # Date for the assessment
            if et_category == "Exam":
                exam_date = random_date(ex_start, ex_end)
                submit_date = None
            else:
                # Assignments: submitted during the semester
                ap = df_academic_period.loc[
                    df_academic_period["academic_period_key"] == period_key
                ].iloc[0]
                sem_start: date = ap["start_date"]
                sem_end: date = ap["exam_period_start"] - timedelta(days=1)
                exam_date = None
                submit_date = random_date(sem_start + timedelta(days=14), sem_end)

            display_date = exam_date if exam_date else submit_date
            exam_dk = date_to_key(display_date) if display_date else None
            submit_dk = date_to_key(submit_date) if submit_date else None

            max_score = 100.0
            raw_score = round(score_pct, 2)

            submission_status = random.choices(
                ["Submitted", "Late", "Non-submission"],
                weights=[0.90, 0.07, 0.03]
            )[0]

            rows.append({
                "exam_result_key": result_key,
                "student_key": student_key,
                "course_key": course_key,
                "exam_type_key": et_key,
                "academic_period_key": period_key,
                "staff_key": random.choice(academic_staff_keys),
                "exam_date_key": exam_dk,
                "submission_date_key": submit_dk,
                "raw_score": raw_score,
                "max_score": max_score,
                "score_percentage": score_pct,
                "grade_letter": grade_letter,
                "grade_points": grade_pts,
                "weighting_pct": weighting,
                "weighted_score": round(score_pct * weighting / 100, 2),
                "attempt_number": 1,
                "is_supplementary": False,
                "submission_status": submission_status,
                "grading_status": "Graded",
            })
            result_key += 1

    df = pd.DataFrame(rows)
    print(f"  fact_exam_results: {len(df):,} rows")
    return df


# ── Generator 13: fact_financial_transactions ─────────────────────────────────

def generate_fact_financial_transactions(
    df_enrollments: pd.DataFrame,
    df_student: pd.DataFrame,
    df_program: pd.DataFrame,
    df_fee_type: pd.DataFrame,
    df_academic_period: pd.DataFrame,
    df_date: pd.DataFrame,
) -> pd.DataFrame:
    print("Generating fact_financial_transactions ...")

    fee_key_map = dict(zip(df_fee_type["fee_type_name"], df_fee_type["fee_type_key"]))
    prog_fees = df_program.set_index("program_key")[
        ["annual_domestic_fee", "annual_international_fee"]
    ].to_dict("index")
    student_meta = df_student.set_index("student_key")[
        ["domestic_international", "program_key", "scholarship_flag"]
    ].to_dict("index")

    period_meta: dict[int, dict] = {}
    for _, p in df_academic_period.iterrows():
        period_meta[int(p["academic_period_key"])] = {
            "start_date": p["start_date"],
            "end_date": p["end_date"],
        }

    # Group enrollments by (student, period)
    active_enroll = df_enrollments[
        ~df_enrollments["enrollment_status"].isin(["Withdrawn", "Deferred"])
        | df_enrollments["withdrew_before_census"]
    ].copy()

    grouped = active_enroll.groupby(["student_key", "academic_period_key"])

    rows = []
    tx_key = 1

    for (student_key, period_key), grp in grouped:
        student_key = int(student_key)
        period_key = int(period_key)
        meta = student_meta.get(student_key, {})
        is_intl = meta.get("domestic_international") == "International"
        prog_key = meta.get("program_key", 1)
        has_scholarship = meta.get("scholarship_flag", False)
        period_start: date = period_meta[period_key]["start_date"]
        period_end: date = period_meta[period_key]["end_date"]
        due_date = period_start + timedelta(days=30)

        credit_points = len(grp) * 4
        prog_fee = prog_fees.get(prog_key, {"annual_domestic_fee": 12000, "annual_international_fee": 33600})
        rate = prog_fee["annual_international_fee"] if is_intl else prog_fee["annual_domestic_fee"]
        tuition_amount = round(rate / 2, 2)  # Per semester = half annual fee

        running_balance = 0.0

        def add_charge(fee_name: str, amount: float, tx_date: date, course_key: int = None):
            nonlocal tx_key, running_balance
            fk = fee_key_map.get(fee_name, 1)
            running_balance += amount
            rows.append({
                "transaction_key": tx_key,
                "student_key": student_key,
                "fee_type_key": fk,
                "academic_period_key": period_key,
                "course_key": course_key,
                "transaction_date_key": date_to_key(tx_date),
                "due_date_key": date_to_key(due_date),
                "transaction_id": f"TX-{tx_key:08d}",
                "transaction_type": "Charge",
                "amount": round(amount, 2),
                "signed_amount": round(amount, 2),
                "currency": "SGD",
                "payment_method": None,
                "reference_number": None,
                "is_overdue": False,
                "days_overdue": 0,
                "outstanding_balance_after": round(running_balance, 2),
            })
            tx_key += 1

        def add_payment(fee_name: str, amount: float, tx_date: date, method: str, ref: str):
            nonlocal tx_key, running_balance
            fk = fee_key_map.get(fee_name, fee_key_map.get("Payment", 6))
            running_balance -= amount
            is_overdue = tx_date > due_date + timedelta(days=30)
            days_overdue = max(0, (tx_date - (due_date + timedelta(days=30))).days) if is_overdue else 0
            rows.append({
                "transaction_key": tx_key,
                "student_key": student_key,
                "fee_type_key": fk,
                "academic_period_key": period_key,
                "course_key": None,
                "transaction_date_key": date_to_key(tx_date),
                "due_date_key": date_to_key(due_date),
                "transaction_id": f"TX-{tx_key:08d}",
                "transaction_type": "Payment",
                "amount": round(amount, 2),
                "signed_amount": round(-amount, 2),
                "currency": "SGD",
                "payment_method": method,
                "reference_number": ref,
                "is_overdue": is_overdue,
                "days_overdue": days_overdue,
                "outstanding_balance_after": round(running_balance, 2),
            })
            tx_key += 1

        # 1. Tuition charge
        add_charge("Tuition", tuition_amount, period_start)

        # 2. Miscellaneous Student Fees
        add_charge("Miscellaneous Student Fees", CONFIG["misc_fees_per_semester"], period_start)

        # 3. Accommodation (20% of students)
        if random.random() < CONFIG["accommodation_rate"]:
            acc_amount = CONFIG["accommodation_monthly_rate"] * 4  # ~4 months per semester
            add_charge("Accommodation", acc_amount, period_start)

        # 4. Library fine (5% of students)
        if random.random() < CONFIG["library_fine_rate"]:
            fine = round(random.uniform(5, CONFIG["library_fine_max"]), 2)
            add_charge("Library Fine", fine, random_date(period_start, period_end))

        # 5. Scholarship credit
        if has_scholarship:
            scholarship_credit = round(tuition_amount * 0.25, 2)
            fk = fee_key_map.get("Scholarship Credit", 7)
            running_balance -= scholarship_credit
            rows.append({
                "transaction_key": tx_key,
                "student_key": student_key,
                "fee_type_key": fk,
                "academic_period_key": period_key,
                "course_key": None,
                "transaction_date_key": date_to_key(period_start),
                "due_date_key": date_to_key(due_date),
                "transaction_id": f"TX-{tx_key:08d}",
                "transaction_type": "Credit",
                "amount": scholarship_credit,
                "signed_amount": round(-scholarship_credit, 2),
                "currency": "SGD",
                "payment_method": None,
                "reference_number": "SCHOLARSHIP",
                "is_overdue": False,
                "days_overdue": 0,
                "outstanding_balance_after": round(running_balance, 2),
            })
            tx_key += 1

        # 6. Payment
        total_charges = running_balance
        r = random.random()
        if r < CONFIG["full_payment_rate"]:
            pay_amount = total_charges
            method = "GIRO" if not is_intl else "Bank Transfer"
            pay_date = random_date(period_start, due_date + timedelta(days=14))
            add_payment("Payment", pay_amount, pay_date, method, fake.bban())
        elif r < CONFIG["full_payment_rate"] + CONFIG["partial_payment_rate"]:
            pay_amount = round(total_charges * random.uniform(0.3, 0.8), 2)
            method = "Direct Debit"
            pay_date = random_date(period_start, period_end)
            add_payment("Payment", pay_amount, pay_date, method, fake.bban())
        # else: no payment — balance remains outstanding

    df = pd.DataFrame(rows)
    print(f"  fact_financial_transactions: {len(df):,} rows")
    return df


# ── Save helpers ──────────────────────────────────────────────────────────────

def save_tables(
    tables: dict[str, pd.DataFrame],
    output_dir: str,
    fmt: str,
) -> None:
    base = Path(output_dir)

    if fmt in ("csv", "both"):
        raw_dir = base / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        for name, df in tables.items():
            path = raw_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            print(f"  Saved {path} ({len(df):,} rows)")

    if fmt in ("parquet", "both"):
        parquet_dir = base / "parquet"
        parquet_dir.mkdir(parents=True, exist_ok=True)
        for name, df in tables.items():
            path = parquet_dir / f"{name}.parquet"
            df.to_parquet(path, index=False)
            print(f"  Saved {path} ({len(df):,} rows)")


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_all() -> dict[str, pd.DataFrame]:
    """Run all 13 generators in FK-dependency order. Returns dict of DataFrames."""
    print("\n=== Fabric IQ Education Demo — Data Generation ===\n")

    dim_date = generate_dim_date()
    dim_department = generate_dim_department()
    dim_program = generate_dim_program(dim_department)
    dim_staff = generate_dim_staff(dim_department)
    dim_course = generate_dim_course(dim_department, dim_staff)
    bridge_course_program = generate_bridge_course_program(dim_course, dim_program, dim_department)
    dim_exam_type = generate_dim_exam_type()
    dim_fee_type = generate_dim_fee_type()
    dim_academic_period = generate_dim_academic_period()
    dim_student = generate_dim_student(dim_program, dim_department)
    fact_enrollments = generate_fact_enrollments(
        dim_student, dim_course, dim_program, dim_academic_period, bridge_course_program, dim_date
    )
    fact_exam_results = generate_fact_exam_results(
        fact_enrollments, dim_exam_type, dim_student, dim_academic_period, dim_staff, dim_date
    )
    fact_financial_transactions = generate_fact_financial_transactions(
        fact_enrollments, dim_student, dim_program, dim_fee_type, dim_academic_period, dim_date
    )

    tables = {
        "dim_date": dim_date,
        "dim_department": dim_department,
        "dim_program": dim_program,
        "dim_staff": dim_staff,
        "dim_course": dim_course,
        "bridge_course_program": bridge_course_program,
        "dim_exam_type": dim_exam_type,
        "dim_fee_type": dim_fee_type,
        "dim_academic_period": dim_academic_period,
        "dim_student": dim_student,
        "fact_enrollments": fact_enrollments,
        "fact_exam_results": fact_exam_results,
        "fact_financial_transactions": fact_financial_transactions,
    }

    print("\n=== Row Count Summary ===")
    for name, df in tables.items():
        print(f"  {name:<38} {len(df):>10,} rows")

    return tables


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic university data for the Fabric IQ Education Demo."
    )
    parser.add_argument(
        "--format",
        choices=["csv", "parquet", "both"],
        default="both",
        help="Output file format (default: both)",
    )
    parser.add_argument(
        "--output-dir",
        default=CONFIG["default_output_dir"],
        help=f"Output directory (default: {CONFIG['default_output_dir']})",
    )
    args = parser.parse_args()

    tables = generate_all()

    print(f"\n=== Saving files to '{args.output_dir}/' (format: {args.format}) ===")
    save_tables(tables, args.output_dir, args.format)
    print("\nDone. Ready to upload to Microsoft Fabric Lakehouse.")


if __name__ == "__main__":
    main()
