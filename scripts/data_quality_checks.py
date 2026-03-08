"""
data_quality_checks.py
======================
Reusable data quality assertion functions.
Used by validate_data.py (local) and Notebook 02 (in Fabric).
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def check_null_pk(df: pd.DataFrame, pk_col: str, table_name: str) -> list[str]:
    """Fail if any primary key value is null."""
    nulls = df[pk_col].isna().sum()
    if nulls:
        return [f"[FAIL] {table_name}.{pk_col}: {nulls} NULL primary key values"]
    return [f"[PASS] {table_name}.{pk_col}: no NULLs"]


def check_pk_unique(df: pd.DataFrame, pk_col: str, table_name: str) -> list[str]:
    """Fail if primary key values are not unique."""
    dupes = df[pk_col].duplicated().sum()
    if dupes:
        return [f"[FAIL] {table_name}.{pk_col}: {dupes} duplicate primary key values"]
    return [f"[PASS] {table_name}.{pk_col}: all values unique"]


def check_composite_pk_unique(
    df: pd.DataFrame, pk_cols: list[str], table_name: str
) -> list[str]:
    """Fail if composite primary key is not unique."""
    dupes = df.duplicated(subset=pk_cols).sum()
    if dupes:
        return [f"[FAIL] {table_name} ({', '.join(pk_cols)}): {dupes} duplicate composite PKs"]
    return [f"[PASS] {table_name} ({', '.join(pk_cols)}): all composite PKs unique"]


def check_fk_integrity(
    child_df: pd.DataFrame,
    child_col: str,
    parent_df: pd.DataFrame,
    parent_col: str,
    child_table: str,
    parent_table: str,
    allow_nulls: bool = False,
) -> list[str]:
    """Fail if any non-null FK value in child is missing from parent."""
    child_vals = child_df[child_col].dropna() if allow_nulls else child_df[child_col]
    parent_vals = set(parent_df[parent_col].tolist())
    orphans = child_vals[~child_vals.isin(parent_vals)]
    if len(orphans):
        return [
            f"[FAIL] {child_table}.{child_col} → {parent_table}.{parent_col}: "
            f"{len(orphans)} orphaned FK values (e.g. {orphans.head(3).tolist()})"
        ]
    return [
        f"[PASS] {child_table}.{child_col} → {parent_table}.{parent_col}: "
        f"all FK values valid"
    ]


def check_row_count(
    df: pd.DataFrame, table_name: str, expected_min: int, expected_max: int = None
) -> list[str]:
    """Fail if row count is outside expected range."""
    n = len(df)
    if n < expected_min:
        return [f"[FAIL] {table_name}: {n:,} rows (expected >= {expected_min:,})"]
    if expected_max and n > expected_max:
        return [f"[FAIL] {table_name}: {n:,} rows (expected <= {expected_max:,})"]
    return [f"[PASS] {table_name}: {n:,} rows"]


def check_score_range(
    df: pd.DataFrame, score_col: str, table_name: str, lo: float = 0.0, hi: float = 100.0
) -> list[str]:
    """Fail if any score value is outside [lo, hi]."""
    out_of_range = ((df[score_col] < lo) | (df[score_col] > hi)).sum()
    if out_of_range:
        return [f"[FAIL] {table_name}.{score_col}: {out_of_range} values outside [{lo}, {hi}]"]
    return [f"[PASS] {table_name}.{score_col}: all values in [{lo:.0f}, {hi:.0f}]"]


def check_allowed_values(
    df: pd.DataFrame, col: str, allowed: list[Any], table_name: str, allow_nulls: bool = True
) -> list[str]:
    """Fail if column contains values not in the allowed list."""
    vals = df[col].dropna() if allow_nulls else df[col]
    invalid = vals[~vals.isin(allowed)]
    if len(invalid):
        return [
            f"[FAIL] {table_name}.{col}: {len(invalid)} invalid values "
            f"(e.g. {invalid.unique()[:3].tolist()})"
        ]
    return [f"[PASS] {table_name}.{col}: all values in allowed set"]


def print_report(results: list[str]) -> int:
    """Print all check results and return count of failures."""
    failures = 0
    for line in results:
        print(f"  {line}")
        if line.startswith("[FAIL]"):
            failures += 1
    return failures
