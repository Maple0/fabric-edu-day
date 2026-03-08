"""
validate_data.py
================
Post-generation validation: checks FK integrity, row counts, null PKs,
value ranges, and allowed-value sets across all 13 tables.

Usage:
  python scripts/validate_data.py --data-dir data
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_quality_checks import (  # noqa: E402
    check_allowed_values,
    check_composite_pk_unique,
    check_fk_integrity,
    check_null_pk,
    check_pk_unique,
    check_row_count,
    check_score_range,
    print_report,
)
from config import CONFIG  # noqa: E402


def load_tables(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all 13 parquet files from data/parquet/."""
    parquet_dir = data_dir / "parquet"
    table_names = [
        "dim_date", "dim_department", "dim_program", "dim_staff", "dim_course",
        "bridge_course_program", "dim_exam_type", "dim_fee_type", "dim_academic_period",
        "dim_student", "fact_enrollments", "fact_exam_results",
        "fact_financial_transactions",
    ]
    tables = {}
    for name in table_names:
        path = parquet_dir / f"{name}.parquet"
        if not path.exists():
            print(f"[WARN] File not found: {path} — skipping")
            continue
        tables[name] = pd.read_parquet(path)
    return tables


def run_all_checks(tables: dict[str, pd.DataFrame]) -> int:
    """Run every check. Returns total failure count."""
    results: list[str] = []
    t = tables  # shorthand

    def section(title: str) -> None:
        results.append(f"\n── {title} ──")

    # ── Row counts ──────────────────────────────────────────────────────────
    section("Row Counts")
    expected_academic_periods = len(CONFIG["academic_years"]) * len(CONFIG["semesters_per_year"])
    results += check_row_count(t["dim_date"],             "dim_date",              3000, 4000)
    results += check_row_count(t["dim_department"],       "dim_department",        len([0]*8), len([0]*8))
    results += check_row_count(t["dim_program"],          "dim_program",           len([0]*12), len([0]*12))
    results += check_row_count(t["dim_staff"],            "dim_staff",             CONFIG["n_staff"])
    results += check_row_count(t["dim_course"],           "dim_course",            CONFIG["n_courses"])
    results += check_row_count(t["bridge_course_program"],"bridge_course_program", CONFIG["n_courses"])
    results += check_row_count(t["dim_exam_type"],        "dim_exam_type",         7, 7)
    results += check_row_count(t["dim_fee_type"],         "dim_fee_type",          8, 8)
    results += check_row_count(t["dim_academic_period"],  "dim_academic_period",   expected_academic_periods, expected_academic_periods)
    results += check_row_count(t["dim_student"],          "dim_student",           CONFIG["n_students"])
    results += check_row_count(t["fact_enrollments"],     "fact_enrollments",      5000)
    results += check_row_count(t["fact_exam_results"],    "fact_exam_results",     50000)
    results += check_row_count(t["fact_financial_transactions"], "fact_financial_transactions", 2000)

    # ── Null & unique PKs ────────────────────────────────────────────────────
    section("Primary Keys — Null Check")
    pk_map = {
        "dim_date": "date_key",
        "dim_department": "department_key",
        "dim_program": "program_key",
        "dim_staff": "staff_key",
        "dim_course": "course_key",
        "dim_exam_type": "exam_type_key",
        "dim_fee_type": "fee_type_key",
        "dim_academic_period": "academic_period_key",
        "dim_student": "student_key",
        "fact_enrollments": "enrollment_key",
        "fact_exam_results": "exam_result_key",
        "fact_financial_transactions": "transaction_key",
    }
    for tbl, pk in pk_map.items():
        if tbl in t:
            results += check_null_pk(t[tbl], pk, tbl)

    section("Primary Keys — Uniqueness")
    for tbl, pk in pk_map.items():
        if tbl in t:
            results += check_pk_unique(t[tbl], pk, tbl)

    section("Composite Primary Key — bridge_course_program")
    if "bridge_course_program" in t:
        results += check_composite_pk_unique(
            t["bridge_course_program"], ["course_key", "program_key"], "bridge_course_program"
        )

    # ── FK integrity ─────────────────────────────────────────────────────────
    section("Foreign Key Integrity")

    # dim_program → dim_department
    results += check_fk_integrity(t["dim_program"], "department_key", t["dim_department"], "department_key", "dim_program", "dim_department")
    # dim_staff → dim_department
    results += check_fk_integrity(t["dim_staff"], "department_key", t["dim_department"], "department_key", "dim_staff", "dim_department")
    # dim_course → dim_department
    results += check_fk_integrity(t["dim_course"], "department_key", t["dim_department"], "department_key", "dim_course", "dim_department")
    # dim_course → dim_staff (coordinator)
    results += check_fk_integrity(t["dim_course"], "coordinator_staff_key", t["dim_staff"], "staff_key", "dim_course", "dim_staff")
    # dim_student → dim_program
    results += check_fk_integrity(t["dim_student"], "program_key", t["dim_program"], "program_key", "dim_student", "dim_program")
    # dim_student → dim_department
    results += check_fk_integrity(t["dim_student"], "department_key", t["dim_department"], "department_key", "dim_student", "dim_department")
    # bridge → dim_course
    results += check_fk_integrity(t["bridge_course_program"], "course_key", t["dim_course"], "course_key", "bridge_course_program", "dim_course")
    # bridge → dim_program
    results += check_fk_integrity(t["bridge_course_program"], "program_key", t["dim_program"], "program_key", "bridge_course_program", "dim_program")
    # fact_enrollments → dim_student
    results += check_fk_integrity(t["fact_enrollments"], "student_key", t["dim_student"], "student_key", "fact_enrollments", "dim_student")
    # fact_enrollments → dim_course
    results += check_fk_integrity(t["fact_enrollments"], "course_key", t["dim_course"], "course_key", "fact_enrollments", "dim_course")
    # fact_enrollments → dim_academic_period
    results += check_fk_integrity(t["fact_enrollments"], "academic_period_key", t["dim_academic_period"], "academic_period_key", "fact_enrollments", "dim_academic_period")
    # fact_enrollments → dim_program
    results += check_fk_integrity(t["fact_enrollments"], "program_key", t["dim_program"], "program_key", "fact_enrollments", "dim_program")
    # fact_enrollments → dim_date (enroll_date_key)
    results += check_fk_integrity(t["fact_enrollments"], "enroll_date_key", t["dim_date"], "date_key", "fact_enrollments", "dim_date (enroll)")
    # fact_exam_results → dim_student
    results += check_fk_integrity(t["fact_exam_results"], "student_key", t["dim_student"], "student_key", "fact_exam_results", "dim_student")
    # fact_exam_results → dim_course
    results += check_fk_integrity(t["fact_exam_results"], "course_key", t["dim_course"], "course_key", "fact_exam_results", "dim_course")
    # fact_exam_results → dim_exam_type
    results += check_fk_integrity(t["fact_exam_results"], "exam_type_key", t["dim_exam_type"], "exam_type_key", "fact_exam_results", "dim_exam_type")
    # fact_exam_results → dim_academic_period
    results += check_fk_integrity(t["fact_exam_results"], "academic_period_key", t["dim_academic_period"], "academic_period_key", "fact_exam_results", "dim_academic_period")
    # fact_exam_results → dim_staff
    results += check_fk_integrity(t["fact_exam_results"], "staff_key", t["dim_staff"], "staff_key", "fact_exam_results", "dim_staff")
    # fact_financial_transactions → dim_student
    results += check_fk_integrity(t["fact_financial_transactions"], "student_key", t["dim_student"], "student_key", "fact_financial_transactions", "dim_student")
    # fact_financial_transactions → dim_fee_type
    results += check_fk_integrity(t["fact_financial_transactions"], "fee_type_key", t["dim_fee_type"], "fee_type_key", "fact_financial_transactions", "dim_fee_type")
    # fact_financial_transactions → dim_academic_period
    results += check_fk_integrity(t["fact_financial_transactions"], "academic_period_key", t["dim_academic_period"], "academic_period_key", "fact_financial_transactions", "dim_academic_period")

    # ── Value ranges ─────────────────────────────────────────────────────────
    section("Value Ranges")
    results += check_score_range(t["fact_exam_results"], "score_percentage", "fact_exam_results")
    results += check_score_range(t["fact_exam_results"], "raw_score", "fact_exam_results")
    results += check_score_range(t["fact_exam_results"], "grade_points", "fact_exam_results", 0.0, 5.0)

    # ── Allowed values ───────────────────────────────────────────────────────
    section("Allowed Values")
    results += check_allowed_values(
        t["fact_exam_results"], "grade_letter", ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "D+", "D", "F"], "fact_exam_results"
    )
    results += check_allowed_values(
        t["dim_student"], "domestic_international", ["Domestic", "International"], "dim_student", allow_nulls=False
    )
    results += check_allowed_values(
        t["dim_student"], "enrolment_status", ["Active", "Graduated", "Withdrawn", "Suspended"], "dim_student", allow_nulls=False
    )
    results += check_allowed_values(
        t["fact_enrollments"], "enrollment_status", ["Enrolled", "Completed", "Failed", "Withdrawn", "Deferred"], "fact_enrollments", allow_nulls=False
    )
    results += check_allowed_values(
        t["fact_financial_transactions"], "transaction_type", ["Charge", "Payment", "Credit", "Refund", "Writeoff"], "fact_financial_transactions", allow_nulls=False
    )

    print_report(results)
    failures = sum(1 for r in results if r.startswith("[FAIL]"))
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate generated data for the Fabric IQ Education Demo."
    )
    parser.add_argument(
        "--data-dir", default="data", help="Directory containing raw/ and parquet/ subdirs"
    )
    args = parser.parse_args()

    print(f"\n=== Fabric IQ Education Demo — Data Validation ===")
    print(f"Loading tables from: {args.data_dir}/parquet/\n")

    tables = load_tables(Path(args.data_dir))
    if not tables:
        print("No parquet files found. Run generate_data.py first.")
        sys.exit(1)

    failures = run_all_checks(tables)

    print(f"\n{'='*52}")
    if failures == 0:
        print("  ALL CHECKS PASSED — data is ready for Fabric Lakehouse upload.")
    else:
        print(f"  {failures} CHECK(S) FAILED — review output above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
