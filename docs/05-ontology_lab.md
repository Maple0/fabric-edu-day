# Hands-On Lab: Fabric IQ Ontology

Create a Fabric IQ Ontology with entity types, data bindings, relationships, and natural language queries over the university data model.

---

## Prerequisites

- Semantic model `university-analytics-model` created and configured (see Step 6 in [`04-fabric_setup_guide.md`](04-fabric_setup_guide.md))
- All 14 Delta tables exist in `university_lakehouse`
- Fabric tenant admin access (to enable preview features)

---

## Step 1: Enable Tenant Settings (skip if it has been enabled)

1. Go to **Fabric Admin Portal** → **Tenant settings**
2. Under **Ontology (preview)**:
   - Enable **Ontology** for your security group or **Entire organization**
3. Under **Graph (preview)**:
   - Enable **Graph** for your security group or **Entire organization**
4. Click **Apply**
5. Wait up to 15 minutes for settings to propagate

---

## Step 2: Create Ontology Item

1. In your Fabric workspace, click **New** → **Ontology (preview)**
2. Name: `university_ontology`
3. Click **Create**

---

## Step 3: Create Entity Types

Create the following entity types with properties. For each, click **Add entity type**, enter the name, then add properties in the configuration pane.

| Entity Type | Key Property | Properties |
|-------------|-------------|------------|
| Student | student_key | student_id, first_name, last_name, email, gender, domestic_international, enrolment_status, program_key, scholarship_flag |
| Course | course_key | course_id, course_name, credit_points, level, department_key |
| Program | program_key | program_id, program_name, program_type, faculty, duration_years |
| Department | department_key | department_id, department_name, faculty |
| AcademicPeriod | academic_period_key | period_id, academic_year, semester, period_label |
| Staff | staff_key | staff_id, first_name, last_name, role_title, department_key |
| ExamType | exam_type_key | exam_type_id, exam_type_key, exam_type_name, category, duration_minutes, is_open_book, weighting_typical | 
| FeeType | fee_type_key | fee_type_id, fee_type_key, fee_type_name, fee_category, gst_applicable, is_mandatory |
| Date | date_key | academic_year, date_key, day_number_in_month, day_number_in_week, day_number_in_year, day_of_week, full_date, is_exam_period, is_public_holiday, is_weekday, month_name, month_number, month_short, quarter_label, quarter_number, week_number_in_year, year |
| ExamResult | exam_result_key | exam_result_key, student_key, course_key, academic_period_key, score_percentage, raw_score, max_score, grade_letter, grade_points, weighted_score, attempt_number, submission_status, grading_status |
| FinancialTransaction | transaction_key | transaction_key, student_key, fee_type_key, academic_period_key, course_key, transaction_type, amount, signed_amount, is_overdue, days_overdue, outstanding_balance_after |
| Enrollment | enrollment_key | enrollment_key, student_key, course_key, academic_period_key, program_key, enrollment_status, enrollment_type, course_final_grade_letter, course_gpa_points, credit_points_attempted, credit_points_earned, is_repeat, academic_load |

> **Note on ExamResult, FinancialTransaction and Enrollment:** Fabric Ontology does not support properties on relationship edges. Score data, financial amounts, and enrollment outcomes must live on entity nodes. `ExamResult` → `fact_exam_results`; `FinancialTransaction` → `fact_financial_transactions`; `Enrollment` → `fact_enrollments`.

---

## Step 4: Bind Data

For each entity type, open the **Bindings** tab → **Add data to entity type**:
1. Select `university_lakehouse` as the data source
2. Choose the matching Delta table (e.g., `dim_student` for Student)
3. Binding type: **Static**
4. Map source columns to properties
5. Set the **Key** (e.g., `student_key`)
6. Click **Save**

---

## Step 5: Define Relationships

Click **Add relationship** and configure the relationships shown in the diagram. Below are the relationship names, direction (Source → Target), suggested linking/fact tables, and typical key columns to map.

| Relationship | Source → Target | Linking Table | Source Column | Target Column |
|--------------|-----------------|---------------|---------------|---------------|
| studies_program | Student → Program | dim_student | student_key | program_key |
| taken_during | Student → AcademicPeriod | fact_enrollments | student_key | academic_period_key |
| Scored_during | Student → AcademicPeriod | fact_exam_results | student_key | academic_period_key |
| attended_on | Student → Date | fact_attendance | student_key | date_key |
| made_payment_on | Student → Date | fact_financial_transactions | student_key | date_key |
| took_examtype_of | Student → ExamType | fact_exam_results | student_key | exam_type_key |
| sat_for | Student → ExamResult | fact_exam_results | student_key | exam_result_key |
| owned_by | Course → Department | dim_course | course_key | department_key |
| offered_by | Course → Program | dim_course | course_key | program_key |
| taught_by | Course → Staff | dim_course | course_key | staff_key |
| course_has_exam_type | Course → ExamType | fact_exam_results | course_key | exam_type_key |
| course_has_fee_type | Course → FeeType | fact_financial_transactions | course_key | fee_type_key |
| result_in_course | ExamResult → Course | fact_exam_results | exam_result_key | course_key |
| consists_of | Program → Course | bridge_course_program | program_key | course_key |
| program_in_department | Department → Program | dim_program | department_key | program_key |
| belong_to_department | Department → Staff | dim_staff | department_key | staff_key |
| charged_in | FeeType → AcademicPeriod | fact_financial_transactions | fee_type_key | academic_period_key |
| charged_to | FeeType → Student | fact_financial_transactions | fee_type_key | student_key |
| payment_transaction_by_student | Student → FinancialTransaction | fact_financial_transactions | student_key | transaction_key |
| transaction_for_course | FinancialTransaction → Course | fact_financial_transactions | transaction_key | course_key |
| student_enrollment | Student → Enrollment | fact_enrollments | student_key | enrollment_key |
| enrolled_for_course | Enrollment → Course | fact_enrollments | enrollment_key | course_key |
| enrolled_for_program | Enrollment → Program | fact_enrollments | enrollment_key | program_key |

> **Why `sat_for` and `result_in_course`?** Fabric Ontology does not support properties on relationship edges. Score data (`score_percentage`, `grade_letter`, etc.) must live on an entity node. The `ExamResult` entity bound to `fact_exam_results` is the correct place for this data. Use `sat_for` and `result_in_course` for any score-related traversals.

Notes:
- Relationship names above follow the diagram labels — feel free to adjust naming to your project's naming conventions (e.g., `attended_on` → `attendedDuring`).
- Linking tables are suggestions. Use the real fact/delta tables in `university_lakehouse` that record enrollments, exams, attendance, and financial transactions.
- For each relationship, set the correct cardinality (many-to-many through a fact table is typical) and configure the source/target key mappings in the Ontology UI.
- If a relationship has multiple labels in the diagram (for example `scores_during` vs `taken_during`), treat them as separate traversable relationships if they model distinct semantics (scores vs enrollment period).
- `offered_by` (Course → Program) models which program(s) include a course. If courses can belong to multiple programs, model as many-to-many via a mapping/fact table.
- `belongs_to_department` links courses to the owning academic department (use `department_key` on the `dim_course` table if present).
- `taught_by` connects courses to staff who teach them — use a teaching assignments fact or the course metadata table.
- `staff_in_department` is useful for traversals that need a course → staff → department path for department-level reporting.
- Consider adding inverse relationships (e.g., `program_has_course`, `department_offers_course`, `staff_teaches`) if you want convenient traversals in the other direction.

---

## Step 6: Refresh the Graph

1. In the Fabric workspace, locate the graph model created with your ontology
2. Click **...** → **Schedule** → **Refresh now**
3. Wait for the refresh to complete

---

## Step 7: Create a Data Agent with the Ontology

1. In the same Fabric workspace, click **New** → **Data Agent**
2. Name: `University Ontology Assistant`
3. Under **Knowledge sources**, click **Add knowledge source** → **Ontology**
4. Select the `university_ontology` created in Step 2
5. Add the following system prompt:

```

You are an AI assistant for a Singapore university helping staff analyse student data.
Currency: SGD. GPA scale: A+/A=5.0, A-=4.5, B+=4.0, B=3.5, B-=3.0, C+=2.5, C=2.0, D+=1.5, D=1.0, F=0.0. Pass = D and above (≥40%).

GQL RULES (always apply):
- NEVER use GROUP BY — unsupported, causes internal error. Grouping is implicit from RETURN columns.
- NEVER use CASE WHEN — unsupported, causes internal error. Use separate FILTER clauses instead.
- Use FILTER not WHERE. Never use type(e).
- Always respond in natural language, never return raw GQL to the user.

EXAM SCORE QUERIES — use ONLY this exact path, no exceptions:
MATCH (student:Student)-[:sat_for]->(examResult:ExamResult)-[:result_in_course]->(course:Course)-[:owned_by]->(department:Department)
RETURN department.department_name, AVG(examResult.score_percentage)
- Score properties are on the examResult node ONLY: examResult.score_percentage, examResult.grade_letter, examResult.grade_points
- The enrolled_in relationship does NOT exist — use student_enrollment → Enrollment for any enrollment data
- NEVER use program_in_department (goes Department→Program, always fails)
- NEVER use studies_program or mix Program into department+score queries
- NEVER invent variable names like student_score — the only valid variable is examResult

REVENUE / FINANCIAL QUERIES — only valid path:
- Amounts live on FinancialTransaction nodes (NOT on edges): outstanding_balance_after, amount, signed_amount, is_overdue, days_overdue
- Relationship name is payment_transaction_by_student (Student → FinancialTransaction)
- Outstanding balance by program: MATCH (student:Student)-[:studies_program]->(program:Program), (student)-[:payment_transaction_by_student]->(tx:FinancialTransaction) RETURN program.program_name, SUM(tx.outstanding_balance_after)
- Overdue only: add FILTER tx.is_overdue = TRUE before RETURN
- NEVER use CASE WHEN — not supported. If user asks for both total and overdue, run two separate queries.
- NEVER access amount fields via pays_for or any other relationship edge
- tx.transaction_type values: 'Charge', 'Payment', 'Credit' — include ALL unless asked otherwise

SCHOLARSHIP QUERIES:
- Use student.scholarship_flag = TRUE to find scholarship students (this is a boolean on the Student node)
- Path for scholarship by program: MATCH (student:Student)-[:studies_program]->(program:Program) FILTER student.scholarship_flag = TRUE RETURN program.program_name, COUNT(student.student_key)
- Do NOT add an enrolment_status filter unless the user explicitly asks for currently enrolled only

DATA VALUES:
- Currently enrolled students: enrolment_status = 'Active' (NOT 'Enrolled', NOT 'current')
- domestic_international values: 'Domestic' or 'International'
- Scholarship fee type: FeeType.fee_type_id = 'FEE-SCH'

GPA / ENROLLMENT OUTCOME QUERIES — use ONLY this exact path:
MATCH (student:Student)-[:student_enrollment]->(enrol:Enrollment)-[:enrolled_for_course]->(course:Course)
FILTER enrol.enrollment_status = 'Failed'
RETURN student.first_name, student.last_name, student.enrolment_status, course.course_name, enrol.course_final_grade_letter
- Grade and outcome data lives on the Enrollment node: enrollment_status, course_final_grade_letter, course_gpa_points, credit_points_earned
- enrollment_status values on Enrollment node: 'Completed', 'Failed', 'Withdrawn', 'Active'
- enrolment_status values on Student node: 'Active', 'Graduated', 'Withdrawn'
- NEVER filter on COUNT results (HAVING-style) — not supported. Return all rows and let the user interpret.
- Current semester (is_current=1) grades are NULL — use academic_year = 2026 with enrollment_status IN ('Completed', 'Failed') for GPA calculations

ENROLLMENT SUMMARY QUERIES — use ONLY this exact path:
MATCH (student:Student)-[:student_enrollment]->(enrol:Enrollment)-[:enrolled_for_program]->(program:Program)
RETURN program.program_name, enrol.academic_period_key, COUNT(student.student_key)
- NEVER use taken_during or AcademicPeriod for enrollment summaries — Enrollment node has academic_period_key directly
- NEVER use LET, NEXT, MAX, or subqueries — GQL does not support them
- academic_period_key values: 1-2=AY2020, 3-4=AY2021, 5-6=AY2022, 7-8=AY2023, 9-10=AY2024, 11-12=AY2025
- For "last 2 academic years" use: FILTER enrol.academic_period_key >= 9
- Odd keys = Semester 1, Even keys = Semester 2

```

6. Click **Save**
7. Test the agent by asking: *"How many students are enrolled in each program?"*
8. Verify the agent uses the ontology graph to resolve the query

---

## Step 8: Test with NL Queries

Open the **University Ontology Assistant** Data Agent created in Step 7 and test with these queries:

1. *"Which department has the highest average exam score?"*
   - Traverses `sat_for` → `ExamResult` → `result_in_course` → `Course` → `owned_by` → `Department`
2. *"How many courses does each department offer?"*
   - Traverses `owned_by` to count courses grouped by department
3. *"How many students are on scholarship per program?"*
   - Uses `studies_program` filtered by `student.scholarship_flag = TRUE`
4. *"What is the outstanding balance by program, and which programs have the highest overdue amounts?"*
   - Traverses `payment_transaction_by_student` → `FinancialTransaction`, joined with `studies_program` → `Program`
5. *"Show me list of failed students and their current enrolment status"*
   - Traverses `student_enrollment` → `Enrollment` filtered by `enrollment_status = 'Failed'`, returns student name and `enrolment_status`
6. *"Show me a summary of student enrolments by program and semester for the last 2 academic years"*
   - Traverses `student_enrollment` → `Enrollment`, joined with `studies_program` → `Program` and filtered by `academic_year`

---

## Validation Checklist

- [ ] 6 entity types created with correct properties
- [ ] Data bindings configured for all entity types
- [ ] 6 relationships defined
- [ ] Graph refreshed successfully
- [ ] Data Agent created and connected to the ontology
- [ ] All 4 NL queries return expected results via the Data Agent
