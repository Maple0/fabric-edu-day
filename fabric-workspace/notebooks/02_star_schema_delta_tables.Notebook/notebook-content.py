# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1668b27e-be25-4f6f-8139-a3ffc5efef0d",
# META       "default_lakehouse_name": "university_lakehouse",
# META       "default_lakehouse_workspace_id": "39778116-f694-4254-9245-676601fe8f6d",
# META       "known_lakehouses": [
# META         {
# META           "id": "1668b27e-be25-4f6f-8139-a3ffc5efef0d"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Notebook 02 — Star Schema Delta Tables
# 
# Reads Parquet files from the Lakehouse, applies explicit PySpark schemas, runs data quality checks, and creates managed Delta tables in the `university` schema.
# 
# **Prerequisites:** Run Notebook 01 first to generate data files.

# CELL ********************

from pyspark.sql.types import (
    StructType, StructField, IntegerType, LongType, StringType,
    FloatType, DoubleType, BooleanType, DateType
)
from pyspark.sql import functions as F

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Define Explicit Schemas
# 
# One `StructType` per table, matching the column names and types from data generation.

# CELL ********************

# ── Dimension Schemas ──

dim_date_schema = StructType([
    StructField("date_key", IntegerType(), False),
    StructField("full_date", DateType(), False),
    StructField("day_of_week", StringType()),
    StructField("day_number_in_week", IntegerType()),
    StructField("day_number_in_month", IntegerType()),
    StructField("day_number_in_year", IntegerType()),
    StructField("week_number_in_year", IntegerType()),
    StructField("month_number", IntegerType()),
    StructField("month_name", StringType()),
    StructField("month_short", StringType()),
    StructField("quarter_number", IntegerType()),
    StructField("quarter_label", StringType()),
    StructField("year", IntegerType()),
    StructField("academic_year", IntegerType()),
    StructField("is_weekday", BooleanType()),
    StructField("is_public_holiday", BooleanType()),
    StructField("is_exam_period", BooleanType()),
])

dim_department_schema = StructType([
    StructField("department_key", IntegerType(), False),
    StructField("department_id", StringType()),
    StructField("department_name", StringType()),
    StructField("faculty", StringType()),
    StructField("head_of_department", StringType()),
    StructField("phone", StringType()),
    StructField("email", StringType()),
    StructField("location_building", StringType()),
    StructField("budget_code", StringType()),
    StructField("is_active", BooleanType()),
])

dim_program_schema = StructType([
    StructField("program_key", IntegerType(), False),
    StructField("program_id", StringType()),
    StructField("program_name", StringType()),
    StructField("program_type", StringType()),
    StructField("duration_years", FloatType()),
    StructField("total_credit_points", IntegerType()),
    StructField("department_key", IntegerType()),
    StructField("faculty", StringType()),
    StructField("igp_score", FloatType(), True),
    StructField("annual_domestic_fee", FloatType()),
    StructField("annual_international_fee", FloatType()),
    StructField("delivery_mode", StringType()),
    StructField("accreditation_body", StringType(), True),
    StructField("is_active", BooleanType()),
])

dim_staff_schema = StructType([
    StructField("staff_key", IntegerType(), False),
    StructField("staff_id", StringType()),
    StructField("first_name", StringType()),
    StructField("last_name", StringType()),
    StructField("email", StringType()),
    StructField("role_title", StringType()),
    StructField("role_category", StringType()),
    StructField("department_key", IntegerType()),
    StructField("employment_type", StringType()),
    StructField("date_joined", DateType()),
    StructField("salary_band", StringType()),
    StructField("is_active", BooleanType()),
])

dim_course_schema = StructType([
    StructField("course_key", IntegerType(), False),
    StructField("course_id", StringType()),
    StructField("course_name", StringType()),
    StructField("credit_points", IntegerType()),
    StructField("level", StringType()),
    StructField("department_key", IntegerType()),
    StructField("coordinator_staff_key", IntegerType()),
    StructField("prerequisite_course_id", StringType(), True),
    StructField("delivery_mode", StringType()),
    StructField("is_core", BooleanType()),
    StructField("is_active", BooleanType()),
    StructField("description", StringType()),
])

dim_exam_type_schema = StructType([
    StructField("exam_type_key", IntegerType(), False),
    StructField("exam_type_id", StringType()),
    StructField("exam_type_name", StringType()),
    StructField("category", StringType()),
    StructField("weighting_typical_pct", FloatType()),
    StructField("duration_minutes", IntegerType(), True),
    StructField("is_open_book", BooleanType(), True),
])

dim_fee_type_schema = StructType([
    StructField("fee_type_key", IntegerType(), False),
    StructField("fee_type_id", StringType()),
    StructField("fee_type_name", StringType()),
    StructField("fee_category", StringType()),
    StructField("is_mandatory", BooleanType()),
    StructField("gst_applicable", BooleanType()),
])

dim_academic_period_schema = StructType([
    StructField("academic_period_key", IntegerType(), False),
    StructField("period_id", StringType()),
    StructField("academic_year", IntegerType()),
    StructField("semester", StringType()),
    StructField("period_label", StringType()),
    StructField("start_date", DateType()),
    StructField("end_date", DateType()),
    StructField("census_date", DateType()),
    StructField("exam_period_start", DateType()),
    StructField("exam_period_end", DateType()),
    StructField("is_current", BooleanType()),
])

dim_student_schema = StructType([
    StructField("student_key", IntegerType(), False),
    StructField("student_id", StringType()),
    StructField("first_name", StringType()),
    StructField("last_name", StringType()),
    StructField("date_of_birth", DateType()),
    StructField("gender", StringType()),
    StructField("email", StringType()),
    StructField("phone", StringType()),
    StructField("address_street", StringType()),
    StructField("address_suburb", StringType()),
    StructField("address_state", StringType()),
    StructField("address_postcode", StringType()),
    StructField("country_of_birth", StringType()),
    StructField("nationality", StringType()),
    StructField("domestic_international", StringType()),
    StructField("enrolment_status", StringType()),
    StructField("enrolment_date", DateType()),
    StructField("expected_graduation_date", DateType()),
    StructField("program_key", IntegerType()),
    StructField("department_key", IntegerType()),
    StructField("academic_year_start", IntegerType()),
    StructField("scholarship_flag", BooleanType()),
    StructField("scholarship_type", StringType(), True),
    StructField("disability_support_flag", BooleanType()),
    StructField("first_in_family_flag", BooleanType()),
    StructField("permanent_resident_flag", BooleanType()),
])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ── Bridge Schema ──

bridge_course_program_schema = StructType([
    StructField("course_key", IntegerType(), False),
    StructField("program_key", IntegerType(), False),
    StructField("course_sequence", IntegerType()),
    StructField("is_core", BooleanType()),
    StructField("year_of_program", IntegerType()),
])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ── Fact Schemas ──

fact_enrollments_schema = StructType([
    StructField("enrollment_key", IntegerType(), False),
    StructField("student_key", IntegerType()),
    StructField("course_key", IntegerType()),
    StructField("academic_period_key", IntegerType()),
    StructField("program_key", IntegerType()),
    StructField("enroll_date_key", IntegerType()),
    StructField("withdraw_date_key", IntegerType(), True),
    StructField("enrollment_status", StringType()),
    StructField("enrollment_type", StringType()),
    StructField("delivery_mode", StringType()),
    StructField("course_final_grade_letter", StringType(), True),
    StructField("course_gpa_points", FloatType(), True),
    StructField("credit_points_attempted", IntegerType()),
    StructField("credit_points_earned", IntegerType()),
    StructField("is_repeat", BooleanType()),
    StructField("withdrew_before_census", BooleanType()),
    StructField("academic_load", FloatType()),
])

fact_exam_results_schema = StructType([
    StructField("exam_result_key", IntegerType(), False),
    StructField("student_key", IntegerType()),
    StructField("course_key", IntegerType()),
    StructField("exam_type_key", IntegerType()),
    StructField("academic_period_key", IntegerType()),
    StructField("staff_key", IntegerType()),
    StructField("exam_date_key", IntegerType(), True),
    StructField("submission_date_key", IntegerType(), True),
    StructField("raw_score", FloatType()),
    StructField("max_score", FloatType()),
    StructField("score_percentage", FloatType()),
    StructField("grade_letter", StringType()),
    StructField("grade_points", FloatType()),
    StructField("weighting_pct", FloatType()),
    StructField("weighted_score", FloatType()),
    StructField("attempt_number", IntegerType()),
    StructField("is_supplementary", BooleanType()),
    StructField("submission_status", StringType()),
    StructField("grading_status", StringType()),
])

fact_financial_transactions_schema = StructType([
    StructField("transaction_key", IntegerType(), False),
    StructField("student_key", IntegerType()),
    StructField("fee_type_key", IntegerType()),
    StructField("academic_period_key", IntegerType()),
    StructField("course_key", IntegerType(), True),
    StructField("transaction_date_key", IntegerType()),
    StructField("due_date_key", IntegerType()),
    StructField("transaction_id", StringType()),
    StructField("transaction_type", StringType()),
    StructField("amount", FloatType()),
    StructField("signed_amount", FloatType()),
    StructField("currency", StringType()),
    StructField("payment_method", StringType(), True),
    StructField("reference_number", StringType(), True),
    StructField("is_overdue", BooleanType()),
    StructField("days_overdue", IntegerType()),
    StructField("outstanding_balance_after", FloatType()),
])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Read Parquet Files with Schemas

# CELL ********************

LAKEHOUSE_FILES = 'Files/parquet'

schema_map = {
    "dim_date": dim_date_schema,
    "dim_department": dim_department_schema,
    "dim_program": dim_program_schema,
    "dim_staff": dim_staff_schema,
    "dim_course": dim_course_schema,
    "bridge_course_program": bridge_course_program_schema,
    "dim_exam_type": dim_exam_type_schema,
    "dim_fee_type": dim_fee_type_schema,
    "dim_academic_period": dim_academic_period_schema,
    "dim_student": dim_student_schema,
    "fact_enrollments": fact_enrollments_schema,
    "fact_exam_results": fact_exam_results_schema,
    "fact_financial_transactions": fact_financial_transactions_schema,
}

tables = {}
for name, schema in schema_map.items():
    path = f'{LAKEHOUSE_FILES}/{name}.parquet'
    tables[name] = spark.read.parquet(path)
    print(f"  Loaded {name}: {tables[name].count():,} rows")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Data Quality Checks
# 
# Verify row counts and null primary keys.

# CELL ********************

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

all_passed = True
for tbl, pk in pk_map.items():
    df = tables[tbl]
    count = df.count()
    nulls = df.filter(F.col(pk).isNull()).count()
    status = 'PASS' if count > 0 and nulls == 0 else 'FAIL'
    if status == 'FAIL':
        all_passed = False
    print(f"  [{status}] {tbl}: {count:,} rows, {nulls} null PKs")

if tbl == list(pk_map.keys())[-1]:
    bridge = tables['bridge_course_program']
    dupes = bridge.count() - bridge.dropDuplicates(["course_key", "program_key"]).count()
    print(f"  [{'PASS' if dupes == 0 else 'FAIL'}] bridge_course_program: {dupes} duplicate composite PKs")

print("\nALL CHECKS PASSED" if all_passed else "\nSOME CHECKS FAILED")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Create Delta Tables
# 
# Write all 13 DataFrames as managed Delta tables in the `university` schema.

# CELL ********************

spark.sql("CREATE SCHEMA IF NOT EXISTS university")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

for name, df in tables.items():
    table_name = f'university.{name}'
    df.write.format('delta') \
        .mode('overwrite') \
        .option('overwriteSchema', 'true') \
        .saveAsTable(table_name)
    print(f"  Created {table_name}")

print("\nAll 13 Delta tables created.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Optimize Fact Tables
# 
# Apply `OPTIMIZE` with `ZORDER BY` on frequently filtered columns.

# CELL ********************

spark.sql("OPTIMIZE university.fact_enrollments ZORDER BY (student_key, academic_period_key)")
spark.sql("OPTIMIZE university.fact_exam_results ZORDER BY (student_key, academic_period_key)")
spark.sql("OPTIMIZE university.fact_financial_transactions ZORDER BY (student_key, academic_period_key)")
print("Fact tables optimized.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Verification

# CELL ********************

spark.sql("SHOW TABLES IN university").show(truncate=False)

print("\n=== Delta Table Row Counts ===")
for name in schema_map.keys():
    count = spark.table(f'university.{name}').count()
    print(f"  university.{name:<38} {count:>10,} rows")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Next Steps
# 
# Proceed to **Notebook 03** to configure the Power BI semantic model with relationships, DAX measures, and RLS.
