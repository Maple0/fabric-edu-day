# Fabric Environment Setup Guide

Pre-demo environment setup instructions for the Fabric IQ Education Demo.

---

## Requirements

| Requirement | Details |
|------------|---------|
| Microsoft Fabric capacity | F8 or higher (required for Copilot and AI features) |
| Azure AD tenant | With Fabric enabled |
| User permissions | Workspace Admin or Contributor |
| Ontology (preview) | Enabled in Fabric tenant admin settings |
| Data Agents | Enabled in Fabric tenant admin settings |
| Browser | Microsoft Edge or Chrome (latest) |

---

## Step 1: Create Fabric Workspace

1. Navigate to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Click **Workspaces** → **New workspace**
3. Name: `EduDay Workspace` (or your preferred name)
4. Under **Advanced**, select your F64+ capacity
5. Click **Apply**

---

## Step 2: Create Lakehouse

1. In your workspace, click **New** → **Lakehouse**
2. Name: `university_lakehouse`
3. Click **Create**

---

## Step 3: Upload Notebooks

Upload all 2 notebooks from the `notebooks/` directory:

1. In the workspace, click **Import** → **Notebook** → **From this computer**
2. Upload each file:
   - `01_data_generation_and_ingestion.ipynb`
   - `02_star_schema_delta_tables.ipynb`

**Alternatively:** Upload Parquet files directly if you want to skip Notebook 01.

---

## Step 4: Attach Lakehouse to Notebooks

For each notebook:

1. Open the notebook
2. Click **Add Lakehouse** (left panel)
3. Select **Existing lakehouse** → choose `university_lakehouse`
4. Click **Add**

The Lakehouse path `/lakehouse/default/` will now resolve correctly in all code cells.

---

## Step 5: Run Notebooks 01 and 02

### Notebook 01: Data Generation & Ingestion

1. Open `01_data_generation_and_ingestion`
2. Click **Run all**
3. Wait for completion (~2-3 minutes)
4. Verify: Navigate to Lakehouse → **Files** → confirm `raw/` and `parquet/` folders contain 13 tables each

### Notebook 02: Star Schema Delta Tables

1. Open `02_star_schema_delta_tables`
2. Click **Run all**
3. Wait for completion (~3-5 minutes)
4. Verify: Navigate to Lakehouse → **Tables** → confirm 13 Delta tables listed
5. Check row counts match expected volumes

---

## Step 6: Create Semantic Model

Follow the detailed instructions in `docs/semantic_model_setup.md`:


---

## Step 7: Create Ontology (Preview)

### 7a: Enable Tenant Settings

1. Go to **Fabric Admin Portal** → **Tenant settings**
2. Under **Ontology (preview)**:
   - Enable **Ontology** for your security group or **Entire organization**
3. Under **Graph (preview)**:
   - Enable **Graph** for your security group or **Entire organization**
4. Click **Apply**
5. Wait up to 15 minutes for settings to propagate

### 7b: Create Ontology Item

1. In your Fabric workspace, click **New** → **Ontology (preview)**
2. Name: `university_ontology`
3. Click **Create**

### 7c: Create Entity Types

Create the following entity types with properties. For each, click **Add entity type**, enter the name, then add properties in the configuration pane.

| Entity Type | Key Property | Properties |
|-------------|-------------|------------|
| Student | student_key | student_id, first_name, last_name, email, gender, domestic_international, enrolment_status, program_key, scholarship_flag |
| Course | course_key | course_id, course_name, credit_points, level, department_key |
| Program | program_key | program_id, program_name, program_type, faculty, duration_years |
| Department | department_key | department_id, department_name, faculty |
| AcademicPeriod | academic_period_key | period_id, academic_year, semester, period_label |
| Staff | staff_key | staff_id, first_name, last_name, role_title, department_key |

### 7d: Bind Data

For each entity type, open the **Bindings** tab → **Add data to entity type**:
1. Select `university_lakehouse` as the data source
2. Choose the matching Delta table (e.g., `dim_student` for Student)
3. Binding type: **Static**
4. Map source columns to properties
5. Set the **Key** (e.g., `student_key`)
6. Click **Save**

### 7e: Define Relationships

Click **Add relationship** and configure:

| Relationship | Source Entity | Target Entity | Linking Table | Source Column | Target Column |
|-------------|-------------|--------------|--------------|--------------|--------------|
| enrolled_in | Student | Course | fact_enrollments | student_key | course_key |
| studies_program | Student | Program | fact_enrollments | student_key | program_key |
| examined_in | Student | Course | fact_exam_results | student_key | course_key |
| pays_for | Student | Course | fact_financial_transactions | student_key | course_key |
| taught_by | Course | Staff | fact_exam_results | course_key | staff_key |
| taken_during | Student | AcademicPeriod | fact_enrollments | student_key | academic_period_key |

### 7f: Refresh the Graph

1. In the Fabric workspace, locate the graph model created with your ontology
2. Click **...** → **Schedule** → **Refresh now**
3. Wait for the refresh to complete

### 7g: Test with NL Queries

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

## Step 8: Create Data Agents

### Staff Agent

1. In the workspace, click **New** → **Data Agent**
2. Name: `University Staff Analytics Assistant`
3. Connect to the `university-analytics-model` semantic model
4. Add the following system prompt:

```
You are an AI assistant for a Singapore university. You help academic staff analyse
student data including enrolments, exam results, and financial transactions.
The data covers academic years 2021-2024.

Use the university schema with tables: dim_student, dim_course, dim_program,
dim_department, dim_staff, dim_academic_period, dim_exam_type, dim_fee_type,
dim_date, bridge_course_program, fact_enrollments, fact_exam_results,
fact_financial_transactions.

Currency is SGD. Grading follows the NUS 5.0 GPA scale (A+/A = 5.0, A- = 4.5,
B+ = 4.0, B = 3.5, B- = 3.0, C+ = 2.5, C = 2.0, D+ = 1.5, D = 1.0, F = 0.0).
Each module is worth 4 Modular Credits (MC). Pass grades are D and above (>= 40%).
```

5. Test with these sample questions:
   1. *"How many students are currently enrolled in each program?"*
   2. *"What is the average GPA across all departments for the current academic year?"*
   3. *"Which courses have the highest failure rates?"*
   4. *"Show me the revenue breakdown by fee type for Semester 1 2024"*
   5. *"Compare domestic vs international student performance in Computer Science courses"*
   6. *"Which students are at risk of academic probation (GPA below 2.0)?"*
   7. *"What is the semester-over-semester enrolment trend for the Business School?"*
   8. *"How much scholarship funding was disbursed per program in the last 2 years?"*
   9. *"Which staff members coordinate the most courses?"*
   10. *"What percentage of students complete their program within the expected duration?"*

### Student Agent

1. Create another Data Agent
2. Name: `Student Self-Service Assistant`
3. Connect to the `university-analytics-model` semantic model
4. Ensure the Student RLS role is active for the connected user
5. Add the following system prompt:

```
You are a personal academic assistant for students at a Singapore university.
You help students understand their academic progress, grades, financial
obligations, and course history. You can only see data for the currently
logged-in student (enforced by Row-Level Security).

Currency is SGD. Grading follows the NUS 5.0 GPA scale (A+/A = 5.0 down
to F = 0.0). Each module is worth 4 Modular Credits (MC).
```

6. Test with sample questions using a test student account (e.g., `stu0042@e.university.edu.sg`):
   1. *"What is my current GPA?"*
   2. *"How many modular credits have I completed so far?"*
   3. *"Show my exam results for the last semester"*
   4. *"Do I have any outstanding fees?"*
   5. *"What courses am I enrolled in this semester?"*
   6. *"How do my grades compare to the course average?"*
   7. *"What is my grade distribution across all courses?"*
   8. *"Have I received any scholarship credits?"*
   9. *"Show my academic progress by semester"*
   10. *"What courses have I failed or withdrawn from?"*

> **RLS verification:** Ask *"show me all students' GPAs"* — the agent should respond that it only has access to this student's records. If it returns data for multiple students, the RLS role is not configured correctly.

---

## Step 9: Pre-Demo Verification

Run through this checklist before presenting:

### Data Layer
- [ ] Lakehouse `university_lakehouse` exists
- [ ] 13 Parquet files under `Files/parquet/`
- [ ] 13 Delta tables under `Tables/`
- [ ] Row counts match expected values

### Semantic Model
- [ ] `university-analytics-model` model exists
- [ ] 13 relationships defined (no warnings)
- [ ] All DAX measures calculate correctly
- [ ] 4 hierarchies created
- [ ] RLS roles configured and tested

### AI Features
- [ ] Ontology created, graph refreshed, NL queries working
- [ ] Staff Data Agent answers questions correctly
- [ ] Student Data Agent scoped to single student
- [ ] All demo prompts tested at least once

### Browser Tabs
Pre-load these tabs for smooth demo transitions:
1. Lakehouse → Tables view
2. Notebook 01 (completed run)
3. Notebook 02 (completed run)
4. Ontology preview experience
5. Staff Data Agent
6. Student Data Agent

---

## Alternative: Upload Pre-Generated Data

If you prefer not to run Notebook 01 in Fabric:

1. Run locally: `python scripts/generate_data.py --format parquet --output-dir data`
2. In the Lakehouse, click **Upload** → **Upload files**
3. Upload all 13 Parquet files from `data/parquet/` to `Files/parquet/`
4. Then run Notebook 02 to create Delta tables from the uploaded Parquet files

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `pip install faker` fails | Check network access from Fabric Runtime; try `%pip install faker --quiet` |
| Lakehouse path not found | Ensure Lakehouse is attached to the notebook (left panel) |
| Delta table write fails | Check workspace capacity is not paused; verify Lakehouse permissions |
| Semantic model refresh error | Verify Delta tables exist; try manual refresh |
| Ontology not available | Enable Ontology (preview) and Graph (preview) in tenant admin settings |
| Data Agent not connecting | Verify semantic model is published; check model permissions |
| RLS not applying | Ensure user is added to the correct role; test with "View as role" |
