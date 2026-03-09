# Data Dictionary — Fabric IQ Education Demo

All tables, columns, data types, and business definitions for the university analytics star schema.

---

## Dimension Tables

### dim_date
Calendar date dimension spanning 2019–2027.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| date_key | INT | No | Primary key (YYYYMMDD format) |
| full_date | DATE | No | Calendar date |
| day_of_week | STRING | No | Day name (Monday–Sunday) |
| day_number_in_week | INT | No | ISO day number (1=Monday, 7=Sunday) |
| day_number_in_month | INT | No | Day of month (1–31) |
| day_number_in_year | INT | No | Day of year (1–366) |
| week_number_in_year | INT | No | Week number (0–53) |
| month_number | INT | No | Month (1–12) |
| month_name | STRING | No | Full month name |
| month_short | STRING | No | Three-letter month abbreviation |
| quarter_number | INT | No | Quarter (1–4) |
| quarter_label | STRING | No | Quarter label (e.g., "Q1 2024") |
| year | INT | No | Calendar year |
| academic_year | INT | No | Academic year (Aug–Jul) |
| is_weekday | BOOLEAN | No | True if Monday–Friday |
| is_public_holiday | BOOLEAN | No | True if public holiday |
| is_exam_period | BOOLEAN | No | True if within exam period dates |

### dim_department
University departments grouped by faculty.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| department_key | INT | No | Primary key (surrogate) |
| department_id | STRING | No | Business key (e.g., "DEPT-CS") |
| department_name | STRING | No | Full department name |
| faculty | STRING | No | Parent faculty name |
| head_of_department | STRING | Yes | Name of department head |
| phone | STRING | Yes | Contact phone number |
| email | STRING | Yes | Department email address |
| location_building | STRING | Yes | Building location |
| budget_code | STRING | Yes | Internal budget code |
| is_active | BOOLEAN | No | Whether department is currently active |

### dim_program
Degree programs offered by the university.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| program_key | INT | No | Primary key (surrogate) |
| program_id | STRING | No | Business key (e.g., "BSCS") |
| program_name | STRING | No | Full program name |
| program_type | STRING | No | Bachelor / Master / Diploma |
| duration_years | DOUBLE | No | Standard duration in years |
| total_credit_points | INT | No | Total credit points required to graduate |
| department_key | INT | No | FK → dim_department |
| faculty | STRING | No | Faculty name (denormalised) |
| igp_score | DOUBLE | Yes | Indicative Grade Profile for admission (null for postgrad) |
| annual_domestic_fee | DOUBLE | No | Annual tuition for domestic students (SGD) |
| annual_international_fee | DOUBLE | No | Annual tuition for international students (SGD) |
| delivery_mode | STRING | Yes | On-campus / Online / Hybrid |
| accreditation_body | STRING | Yes | Accrediting organisation (e.g., MOE Singapore) |
| is_active | BOOLEAN | No | Whether program is currently offered |

### dim_staff
University staff members (academic and administrative).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| staff_key | INT | No | Primary key (surrogate) |
| staff_id | STRING | No | Business key (e.g., "STAFF-0001") |
| first_name | STRING | No | First name |
| last_name | STRING | No | Last name |
| email | STRING | No | Staff email address |
| role_title | STRING | No | Job title (e.g., Professor, Lecturer) |
| role_category | STRING | No | Academic / Research / Administrative |
| department_key | INT | No | FK → dim_department |
| employment_type | STRING | No | Full-time / Part-time / Casual |
| date_joined | DATE | No | Date staff member joined |
| salary_band | STRING | No | Salary band (Band A–F) |
| is_active | BOOLEAN | No | Whether currently employed |

### dim_course
Individual units of study (courses/subjects).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| course_key | INT | No | Primary key (surrogate) |
| course_id | STRING | No | Business key (e.g., "COMP1000") |
| course_name | STRING | No | Course title |
| credit_points | INT | No | Modular Credit value (typically 4 MC) |
| level | STRING | No | Undergraduate / Postgraduate |
| department_key | INT | No | FK → dim_department |
| coordinator_staff_key | INT | No | FK → dim_staff (course coordinator) |
| prerequisite_course_id | STRING | Yes | Prerequisite course ID (simplified) |
| delivery_mode | STRING | Yes | On-campus / Online / Hybrid |
| is_core | BOOLEAN | No | Whether course is a core requirement |
| is_active | BOOLEAN | No | Whether course is currently offered |
| description | STRING | Yes | Course description text |

### dim_exam_type
Assessment types with typical weightings.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| exam_type_key | INT | No | Primary key (surrogate) |
| exam_type_id | STRING | No | Business key (e.g., "EXAM-FIN") |
| exam_type_name | STRING | No | Assessment name (Final Exam, Midterm, etc.) |
| category | STRING | No | Exam / Assessment |
| weighting_typical_pct | DOUBLE | No | Typical weighting percentage |
| duration_minutes | INT | Yes | Duration in minutes (null for take-home) |
| is_open_book | BOOLEAN | Yes | Whether open-book (null for assignments) |

### dim_fee_type
Fee categories for financial transactions.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| fee_type_key | INT | No | Primary key (surrogate) |
| fee_type_id | STRING | No | Business key (e.g., "FEE-TUI") |
| fee_type_name | STRING | No | Fee name (Tuition, Miscellaneous Student Fees, etc.) |
| fee_category | STRING | No | Charge / Payment / Credit |
| is_mandatory | BOOLEAN | No | Whether fee is mandatory |
| gst_applicable | BOOLEAN | No | Whether GST applies |

### dim_academic_period
Academic semesters (2021–2024, 2 per year = 8 total).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| academic_period_key | INT | No | Primary key (surrogate) |
| period_id | STRING | No | Business key (e.g., "2024-S1") |
| academic_year | INT | No | Year (2021–2024) |
| semester | STRING | No | "Semester 1" or "Semester 2" |
| period_label | STRING | No | Display label (e.g., "Semester 1 2024") |
| start_date | DATE | No | Semester start date |
| end_date | DATE | No | Semester end date |
| census_date | DATE | No | Census date (last date to withdraw without penalty) |
| exam_period_start | DATE | No | Exam period start |
| exam_period_end | DATE | No | Exam period end |
| is_current | BOOLEAN | No | Whether this is the current semester |

### dim_student
Student records with demographics and enrolment details.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| student_key | INT | No | Primary key (surrogate) |
| student_id | STRING | No | Business key (e.g., "STU-2021-0042") |
| first_name | STRING | No | First name |
| last_name | STRING | No | Last name |
| date_of_birth | DATE | No | Date of birth |
| gender | STRING | No | Male / Female / Non-binary / Prefer not to say |
| email | STRING | No | Student email (used for RLS) |
| phone | STRING | Yes | Phone number |
| address_street | STRING | Yes | Street address |
| address_suburb | STRING | Yes | Suburb |
| address_state | STRING | Yes | State abbreviation |
| address_postcode | STRING | Yes | Postcode |
| country_of_birth | STRING | No | Country of birth |
| nationality | STRING | No | Nationality |
| domestic_international | STRING | No | "Domestic" or "International" |
| enrolment_status | STRING | No | Active / Graduated / Withdrawn / Suspended |
| enrolment_date | DATE | No | Date of initial enrolment |
| expected_graduation_date | DATE | Yes | Expected graduation date |
| program_key | INT | No | FK → dim_program |
| department_key | INT | No | FK → dim_department |
| academic_year_start | INT | No | Year student first enrolled |
| scholarship_flag | BOOLEAN | No | Whether student has a scholarship |
| scholarship_type | STRING | Yes | Scholarship name (null if no scholarship) |
| disability_support_flag | BOOLEAN | No | Whether registered for disability support |
| first_in_family_flag | BOOLEAN | No | First in family to attend university |
| permanent_resident_flag | BOOLEAN | No | Singapore Permanent Resident |

---

## Bridge Table

### bridge_course_program
Resolves many-to-many between courses and programs.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| course_key | INT | No | FK → dim_course (composite PK) |
| program_key | INT | No | FK → dim_program (composite PK) |
| course_sequence | INT | No | Order within the program structure |
| is_core | BOOLEAN | No | Core requirement vs elective |
| year_of_program | INT | No | Typical year of study (1, 2, 3, or 4) |

---

## Fact Tables

### fact_enrollments
One row per student per course per academic period.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| enrollment_key | INT | No | Primary key (surrogate) |
| student_key | INT | No | FK → dim_student |
| course_key | INT | No | FK → dim_course |
| academic_period_key | INT | No | FK → dim_academic_period |
| program_key | INT | No | FK → dim_program |
| enroll_date_key | INT | No | FK → dim_date (enrolment date) |
| withdraw_date_key | INT | Yes | FK → dim_date (withdrawal date, null if not withdrawn) |
| enrollment_status | STRING | No | Enrolled / Completed / Failed / Withdrawn / Deferred |
| enrollment_type | STRING | No | Full-time (always in this demo) |
| delivery_mode | STRING | Yes | On-campus / Online / Hybrid |
| course_final_grade_letter | STRING | Yes | Final course grade (A+ through F on NUS scale, null if withdrawn) |
| course_gpa_points | DOUBLE | Yes | GPA points for the course (0.0–5.0) |
| credit_points_attempted | INT | No | Modular Credits attempted (typically 4 MC) |
| credit_points_earned | INT | No | Modular Credits earned (0 if failed/withdrawn) |
| is_repeat | BOOLEAN | No | Whether this is a repeat enrolment |
| withdrew_before_census | BOOLEAN | No | Whether withdrawal was before census date |
| academic_load | DOUBLE | No | Academic load factor (1.0 = full) |

### fact_exam_results
One row per student per assessment per course per period.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| exam_result_key | INT | No | Primary key (surrogate) |
| student_key | INT | No | FK → dim_student |
| course_key | INT | No | FK → dim_course |
| exam_type_key | INT | No | FK → dim_exam_type |
| academic_period_key | INT | No | FK → dim_academic_period |
| staff_key | INT | No | FK → dim_staff (grading staff) |
| exam_date_key | INT | Yes | FK → dim_date (exam date, null for assignments) |
| submission_date_key | INT | Yes | FK → dim_date (submission date, null for exams) |
| raw_score | DOUBLE | No | Raw score achieved |
| max_score | DOUBLE | No | Maximum possible score (100) |
| score_percentage | DOUBLE | No | Score as percentage (0–100) |
| grade_letter | STRING | No | Grade on NUS 5.0 scale (A+/A/A-/B+/B/B-/C+/C/D+/D/F) |
| grade_points | DOUBLE | No | GPA points (5.0/4.5/4.0/3.5/3.0/2.5/2.0/1.5/1.0/0.0) |
| weighting_pct | DOUBLE | No | Assessment weighting percentage |
| weighted_score | DOUBLE | No | Score × weighting / 100 |
| attempt_number | INT | No | Attempt number (1 for first attempt) |
| is_supplementary | BOOLEAN | No | Whether this is a supplementary assessment |
| submission_status | STRING | No | Submitted / Late / Non-submission |
| grading_status | STRING | No | Graded (always in this demo) |

### fact_financial_transactions
One row per financial transaction line item.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| transaction_key | INT | No | Primary key (surrogate) |
| student_key | INT | No | FK → dim_student |
| fee_type_key | INT | No | FK → dim_fee_type |
| academic_period_key | INT | No | FK → dim_academic_period |
| course_key | INT | Yes | FK → dim_course (null for non-course fees) |
| transaction_date_key | INT | No | FK → dim_date (transaction date) |
| due_date_key | INT | No | FK → dim_date (payment due date) |
| transaction_id | STRING | No | Business key (e.g., "TX-00000001") |
| transaction_type | STRING | No | Charge / Payment / Credit |
| amount | DOUBLE | No | Absolute amount (SGD) |
| signed_amount | DOUBLE | No | Signed amount (+charge, -payment/credit) |
| currency | STRING | No | Currency code ("SGD") |
| payment_method | STRING | Yes | GIRO / Bank Transfer / Direct Debit (null for charges) |
| reference_number | STRING | Yes | Payment reference number |
| is_overdue | BOOLEAN | No | Whether payment is overdue |
| days_overdue | INT | No | Number of days overdue (0 if not overdue) |
| outstanding_balance_after | DOUBLE | No | Running balance after this transaction |

---

## Grade Scale Reference — NUS 5.0 Scale

| Grade | Score Range | GPA Points |
|-------|-----------|------------|
| A+ | 85–100% | 5.0 |
| A | 80–84% | 5.0 |
| A- | 75–79% | 4.5 |
| B+ | 70–74% | 4.0 |
| B | 65–69% | 3.5 |
| B- | 60–64% | 3.0 |
| C+ | 55–59% | 2.5 |
| C | 50–54% | 2.0 |
| D+ | 45–49% | 1.5 |
| D | 40–44% | 1.0 |
| F | 0–39% | 0.0 |

## Data Volume Summary

| Table | Rows | Type |
|-------|------|------|
| dim_date | ~3,300 | Dimension |
| dim_department | 8 | Dimension |
| dim_program | 12 | Dimension |
| dim_staff | 80 | Dimension |
| dim_course | 60 | Dimension |
| bridge_course_program | ~380 | Bridge |
| dim_exam_type | 7 | Dimension |
| dim_fee_type | 8 | Dimension |
| dim_academic_period | 8 | Dimension |
| dim_student | 520 | Dimension |
| fact_enrollments | ~10,900 | Fact |
| fact_exam_results | ~72,000 | Fact |
| fact_financial_transactions | ~7,500 | Fact |
