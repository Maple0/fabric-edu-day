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

| Relationship | Source → Target | Suggested Linking Table | Typical Source Key | Typical Target Key |
|--------------|-----------------|-------------------------|--------------------|--------------------|
| enrolled_in | Student → Course | fact_enrollments | student_key | course_key |
| examined_in | Student → Course | fact_exam_results | student_key | course_key |
| pays_for | Student → Course | fact_financial_transactions | student_key | course_key |
| studies_program | Student → Program | dim_student or fact_enrollments | student_key | program_key |
| scores_during | Student → AcademicPeriod | fact_exam_results | student_key | academic_period_key |
| taken_during | Student → AcademicPeriod | fact_enrollments | student_key | academic_period_key |
| attended_on | Student → Date | fact_attendance or fact_course_events | student_key | date_key |
| made_payment_on | Student → Date | fact_financial_transactions | student_key | date_key |
| charged_to | Student → FeeType | fact_financial_transactions | student_key | fee_type_key |
| has_exam_type | Student → ExamType | fact_exam_results | student_key | exam_type_key |
| offered_by | Course → Program | dim_course or dim_program | course_key | program_key |
| belongs_to_department | Course → Department | dim_course | course_key | department_key |
| taught_by | Course → Staff | fact_teaching_assignments or dim_course | course_key | staff_key |
| staff_in_department | Staff → Department | dim_staff | staff_key | department_key |
| belong_to_department | Staff → Department | dim_staff | staff_key | department_key |
| consists_of | Program → Course | dim_program_course or mapping table | program_key | course_key |
| belongs_to_department | Program → Department | dim_program | program_key | department_key |
| owned_by | Course → Department | dim_course | course_key | department_key |
| offered_during | AcademicPeriod → Course | fact_course_offerings or schedule | academic_period_key | course_key |
| charged_during | AcademicPeriod → FeeType | fact_financial_transactions | academic_period_key | fee_type_key |
| course_has_exam_type | Course → ExamType | fact_exam_results | course_key | exam_type_key |
| took_examtype_of | Student → ExamType | fact_exam_results | student_key | exam_type_key |
| course_has_fee_type | Course → FeeType | fact_financial_transactions | course_key | fee_type_key |
| charged_to | FeeType → Student | fact_financial_transactions | fee_type_key | student_key |
| charged_in | AcademicPeriod → FeeType | fact_financial_transactions | academic_period_key | fee_type_key |
| attended_on | Student → Date | fact_attendance or fact_course_events | student_key | date_key |
| made_payment_on | Student → Date | fact_financial_transactions | student_key | date_key |

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

You are an AI assistant for a Singapore university.
You help academic staff analyse enrolments, grades, and financial transactions.

STRICT GRAPH USAGE RULES (MANDATORY):

1. Academic time-based filtering for semester or academic year MUST ALWAYS be done using:
   (FeeType)-[:charged_in]->(AcademicPeriod)

2. DO NOT use Date, transaction_date, or any Date-based entity
   for semester or academic-year filtering in revenue queries.

3. When answering revenue questions by semester or academic year:
   - AcademicPeriod.semester uses full names such as "Semester 1" or "Semester 2"
   - AcademicPeriod.academic_year must be used
   - The relationship :charged_in MUST appear in the MATCH clause

4. The AI MUST NOT generate queries that bypass the charged_in relationship.

5. Output only a SINGLE pure GQL query:
   - No JSON wrappers
   - No entitySelector
   - Use FILTER (not WHERE)
   - Do not use type(e)
   - Do not use GROUP BY unless explicitly required

6. Use relationships ONLY from:
   fact_financial_transactions, fact_enrollments, fact_exam_results,
   bridge_course_program

Currency is SGD.Grading follows the NUS 5.0 GPA scale (A+/A = 5.0, A- = 4.5, B+ = 4.0, B = 3.5, B- = 3.0, C+ = 2.5, C = 2.0, D+ = 1.5, D = 1.0, F = 0.0). Each module is worth 4 Modular Credits (MC). Pass grades are D and above (>= 40%), grades below D and (<40%) are considered as failure grades.

IMPORTANT DATA FILTERING GUIDELINES:

- Student enrollment status: Use "Active" in student.enrolment_status to identify currently enrolled students (NOT "Enrolled"). Valid status values are: "Active", "Graduated", "Withdrawn", "Suspended"
- Semester references: When filtering by semester in AcademicPeriod.semester, always use full names like "Semester 1" or "Semester 2" , do NOT use value '1' or '2' to filter the semester
- Financial transactions: For revenue analysis, include ALL transaction types (Charge, Payment, Credit) from fact_financial_transactions.transaction_type unless specifically asked to filter by payment type
- Scholarship queries: Use FeeType.fee_type_id = 'FEE-SCH' when filtering for scholarship-related transactions

CURRENTLY ENROLLED

- Always consider rows where enrollment_status = 'Active'

CRITICAL — GPA AND GRADE QUERIES:

- The current semester (AcademicPeriod.is_current = 1) is still in progress. Students enrolled in the current semester have enrollment_status = 'Enrolled' and their course_gpa_points and course_final_grade_letter are NULL because grades are not finalised yet.
- NEVER use is_current = 1 when calculating GPA or grade averages — it will return no meaningful data.
- When asked about "current academic year" GPA or grades, filter by AcademicPeriod.academic_year = 2026 (the latest academic year) AND fact_enrollments.enrollment_status IN ('Completed', 'Failed'). This returns only semesters where grades have been finalised.
- When asked about "current semester" GPA or grades, explain that the current semester is still in progress and grades are not yet available. Offer to show grades from the most recently completed semester instead.
- Always compute GPA only from rows where course_gpa_points IS NOT NULL and enrollment_status IN ('Completed', 'Failed').
- fact_enrollments.enrollment_status values: 'Enrolled' (in-progress, no grade yet), 'Completed' (passed), 'Failed' (failed), 'Withdrawn' (dropped), 'Deferred' (deferred). Only 'Completed' and 'Failed' have GPA values.

```

6. Click **Save**
7. Test the agent by asking: *"How many students are enrolled in each program?"*
8. Verify the agent uses the ontology graph to resolve the query

---

## Step 8: Test with NL Queries

Open the **University Ontology Assistant** Data Agent created in Step 7 and test with these queries:

1. *"Show me a summary of student enrolments by program and semester for the last 2 academic years"*
   - Traverses `enrolled_in`, `studies_program`, and `taken_during` relationships
2. *"Compare the average exam scores between domestic and international students across all departments"*
   - Uses `examined_in` relationship and Student `domestic_international` property
3. *"What is the outstanding balance by program, and which programs have the highest overdue amounts?"*
   - Follows `pays_for` and `studies_program` relationships for financial aggregation
4. *"Show me students who have failed more than 2 courses and their current enrolment status"*
   - Cross-domain reasoning combining enrolment outcomes with student status

---

## Validation Checklist

- [ ] 6 entity types created with correct properties
- [ ] Data bindings configured for all entity types
- [ ] 6 relationships defined
- [ ] Graph refreshed successfully
- [ ] Data Agent created and connected to the ontology
- [ ] All 4 NL queries return expected results via the Data Agent
