"""
Centralised configuration for the Fabric IQ Education Demo data generation.
All parameters that control data shape, volume, distributions, and fees are
defined here so that generate_data.py and all Fabric notebooks stay in sync.

Context: Singapore university (NUS-style grading, SGD, Aug-start academic year).
"""

CONFIG = {
    # ── Volume ──────────────────────────────────────────────────────────────
    "n_students": 520,
    "n_departments": 8,
    "n_programs": 12,
    "n_courses": 60,
    "n_staff": 80,
    "academic_years": [2021, 2022, 2023, 2024],
    "semesters_per_year": ["Semester 1", "Semester 2"],

    # ── Averages per student per semester ────────────────────────────────────
    "avg_courses_per_student_per_semester": 5,
    "max_courses_per_student_per_semester": 6,

    # ── Score distributions ──────────────────────────────────────────────────
    # Bimodal: small fail cluster + large pass cluster
    "score_fail_mean": 25,
    "score_fail_std": 10,
    "score_fail_min": 0,
    "score_fail_max": 39,
    "score_pass_mean": 68,
    "score_pass_std": 14,
    "score_pass_min": 40,
    "score_pass_max": 100,
    "fail_rate": 0.08,           # 8% of results are failing
    "international_penalty": 2,  # International students score 2pts lower on average
    "repeat_bonus": 5,           # Repeat attempt students score 5pts higher on average

    # ── Singapore NUS 5.0 GPA grade boundaries ────────────────────────────────
    "grade_boundaries": [
        {"min": 85, "max": 100, "letter": "A+", "points": 5.0},
        {"min": 80, "max": 84,  "letter": "A",  "points": 5.0},
        {"min": 75, "max": 79,  "letter": "A-", "points": 4.5},
        {"min": 70, "max": 74,  "letter": "B+", "points": 4.0},
        {"min": 65, "max": 69,  "letter": "B",  "points": 3.5},
        {"min": 60, "max": 64,  "letter": "B-", "points": 3.0},
        {"min": 55, "max": 59,  "letter": "C+", "points": 2.5},
        {"min": 50, "max": 54,  "letter": "C",  "points": 2.0},
        {"min": 45, "max": 49,  "letter": "D+", "points": 1.5},
        {"min": 40, "max": 44,  "letter": "D",  "points": 1.0},
        {"min": 0,  "max": 39,  "letter": "F",  "points": 0.0},
    ],

    # ── Enrolment mix ────────────────────────────────────────────────────────
    "domestic_ratio": 0.70,      # 70% domestic (SG citizens + PRs), 30% international
    "enrolment_status_weights": {
        "Active": 0.65,
        "Graduated": 0.25,
        "Withdrawn": 0.07,
        "Suspended": 0.03,
    },
    "withdrawal_rate": 0.05,     # 5% of course enrollments end in withdrawal
    "scholarship_rate_domestic": 0.15,
    "repeat_rate": 0.04,         # 4% of enrollments are repeat attempts

    # ── Financial rates (SGD) ──────────────────────────────────────────────────
    "misc_fees_per_semester": 150.00,              # Miscellaneous Student Fees
    "domestic_fee_per_credit_point": 300,           # Per Modular Credit (MC) per year base rate
    "international_multiplier": 2.8,                # International fees ~ 2.8x domestic
    "accommodation_monthly_rate": 500,              # Campus hostel monthly rate
    "accommodation_rate": 0.20,                     # 20% of students have accommodation charge
    "library_fine_rate": 0.05,                      # 5% of students incur a library fine
    "library_fine_max": 30.00,
    "full_payment_rate": 0.80,                      # 80% pay in full
    "partial_payment_rate": 0.15,                   # 15% partial payment
    # remaining 5% make no payment (outstanding balance)

    # ── Academic calendar (Singapore: S1 Aug-Dec, S2 Jan-May) ──────────────────
    # Defined as (month, day) relative to each year
    "semester1_start_mmdd": (8, 12),
    "semester1_end_mmdd": (12, 6),
    "semester1_census_mmdd": (9, 13),
    "semester1_exam_start_mmdd": (11, 25),
    "semester1_exam_end_mmdd": (12, 6),
    "semester2_start_mmdd": (1, 13),
    "semester2_end_mmdd": (5, 9),
    "semester2_census_mmdd": (2, 14),
    "semester2_exam_start_mmdd": (4, 28),
    "semester2_exam_end_mmdd": (5, 9),

    # ── Faker / randomness ────────────────────────────────────────────────────
    "faker_locale": "en_US",
    "seed": 42,

    # ── Date dimension range ─────────────────────────────────────────────────
    "date_dim_start": "2019-01-01",
    "date_dim_end": "2027-12-31",

    # ── Output ───────────────────────────────────────────────────────────────
    "default_output_dir": "data",
}

# ── Static reference data ──────────────────────────────────────────────────────

DEPARTMENTS = [
    {"id": "DEPT-CS",   "name": "Computer Science",          "faculty": "School of Computing"},
    {"id": "DEPT-ENG",  "name": "Electrical Engineering",    "faculty": "Faculty of Engineering"},
    {"id": "DEPT-BUS",  "name": "Business Administration",   "faculty": "Business School"},
    {"id": "DEPT-ACC",  "name": "Accountancy",               "faculty": "Business School"},
    {"id": "DEPT-NUR",  "name": "Nursing",                   "faculty": "Faculty of Health Sciences"},
    {"id": "DEPT-MED",  "name": "Biomedical Sciences",       "faculty": "Faculty of Health Sciences"},
    {"id": "DEPT-EDU",  "name": "Education",                 "faculty": "Faculty of Arts & Social Sciences"},
    {"id": "DEPT-LAW",  "name": "Law",                       "faculty": "Faculty of Law"},
]

PROGRAMS = [
    {"id": "BSCS",  "name": "Bachelor of Computing",                       "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-CS",  "igp_score": 82.5},
    {"id": "BSEE",  "name": "Bachelor of Engineering (EE)",                 "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-ENG", "igp_score": 80.0},
    {"id": "BBAD",  "name": "Bachelor of Business Administration",          "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-BUS", "igp_score": 75.0},
    {"id": "BACC",  "name": "Bachelor of Accountancy",                      "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-ACC", "igp_score": 76.25},
    {"id": "BNUR",  "name": "Bachelor of Science (Nursing)",                "type": "Bachelor", "years": 3.0, "dept_id": "DEPT-NUR", "igp_score": 70.0},
    {"id": "BMED",  "name": "Bachelor of Science (Biomedical Sciences)",    "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-MED", "igp_score": 85.0},
    {"id": "BEDU",  "name": "Bachelor of Arts (Education)",                 "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-EDU", "igp_score": 67.5},
    {"id": "BLAW",  "name": "Bachelor of Laws",                             "type": "Bachelor", "years": 4.0, "dept_id": "DEPT-LAW", "igp_score": 87.5},
    {"id": "MBAD",  "name": "Master of Business Administration",            "type": "Master",   "years": 1.5, "dept_id": "DEPT-BUS", "igp_score": None},
    {"id": "MDSCI", "name": "Master of Computing (Data Science)",           "type": "Master",   "years": 2.0, "dept_id": "DEPT-CS",  "igp_score": None},
    {"id": "MFIN",  "name": "Master of Science (Finance)",                  "type": "Master",   "years": 1.5, "dept_id": "DEPT-ACC", "igp_score": None},
    {"id": "PGDIP", "name": "Postgraduate Diploma in Education",            "type": "Diploma",  "years": 1.0, "dept_id": "DEPT-EDU", "igp_score": None},
]

EXAM_TYPES = [
    {"id": "EXAM-FIN", "name": "Final Exam",     "category": "Exam",       "weight": 50.0, "duration": 120, "open_book": False},
    {"id": "EXAM-MID", "name": "Midterm Exam",   "category": "Exam",       "weight": 30.0, "duration": 60,  "open_book": False},
    {"id": "ASGN-1",   "name": "Assignment 1",   "category": "Assessment", "weight": 15.0, "duration": None, "open_book": None},
    {"id": "ASGN-2",   "name": "Assignment 2",   "category": "Assessment", "weight": 20.0, "duration": None, "open_book": None},
    {"id": "QUIZ",     "name": "Quiz",            "category": "Assessment", "weight": 10.0, "duration": 30,  "open_book": False},
    {"id": "PRAC",     "name": "Practical",       "category": "Assessment", "weight": 20.0, "duration": 90,  "open_book": True},
    {"id": "PRES",     "name": "Presentation",    "category": "Assessment", "weight": 15.0, "duration": None, "open_book": None},
]

FEE_TYPES = [
    {"id": "FEE-TUI",  "name": "Tuition",                        "category": "Charge",  "mandatory": True,  "gst": False},
    {"id": "FEE-MISC", "name": "Miscellaneous Student Fees",     "category": "Charge",  "mandatory": True,  "gst": True},
    {"id": "FEE-ACC",  "name": "Accommodation",                  "category": "Charge",  "mandatory": False, "gst": True},
    {"id": "FEE-LIB",  "name": "Library Fine",                   "category": "Charge",  "mandatory": False, "gst": False},
    {"id": "FEE-PARK", "name": "Parking",                        "category": "Charge",  "mandatory": False, "gst": True},
    {"id": "FEE-PAY",  "name": "Payment",                        "category": "Payment", "mandatory": False, "gst": False},
    {"id": "FEE-SCH",  "name": "Scholarship Credit",             "category": "Credit",  "mandatory": False, "gst": False},
    {"id": "FEE-REF",  "name": "Refund",                         "category": "Credit",  "mandatory": False, "gst": False},
]
