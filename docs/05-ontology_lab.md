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

## Step 7: Test with NL Queries

Open the ontology preview experience and test with these queries:

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
- [ ] All 4 NL queries return expected results
