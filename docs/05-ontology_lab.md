# Hands-On Lab: Fabric IQ Ontology

Create a Fabric IQ Ontology with entity types, data bindings, relationships, and natural language queries over the university data model.

---

## Prerequisites

- Semantic model `university-analytics-model` created and configured (see Step 6 in [`04-fabric_setup_guide.md`](04-fabric_setup_guide.md))
- All 13 Delta tables exist in `university_lakehouse`
- Fabric tenant admin access (to enable preview features)

---

## Step 1: Enable Tenant Settings

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

Click **Add relationship** and configure:

| Relationship | Source Entity | Target Entity | Linking Table | Source Column | Target Column |
|-------------|-------------|--------------|--------------|--------------|--------------|
| enrolled_in | Student | Course | fact_enrollments | student_key | course_key |
| studies_program | Student | Program | fact_enrollments | student_key | program_key |
| examined_in | Student | Course | fact_exam_results | student_key | course_key |
| pays_for | Student | Course | fact_financial_transactions | student_key | course_key |
| taught_by | Course | Staff | fact_exam_results | course_key | staff_key |
| taken_during | Student | AcademicPeriod | fact_enrollments | student_key | academic_period_key |

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
