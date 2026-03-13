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

Upload all 4 notebooks from the `notebooks/` directory:

1. In the workspace, click **Import** → **Notebook** → **From this computer**
2. Upload each file:
   - `01_data_generation_and_ingestion.ipynb`
   - `02_star_schema_delta_tables.ipynb`
   - `03_update_student_records_RLS.ipynb`
   - `04_ingest_publicholidays.ipynb`

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

## Step 5: Run Notebooks

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

### Notebook 03: Update Student Records for RLS

1. Open `03_update_student_records_RLS`
2. Click **Run all**
3. This updates a student email to match the current Fabric sign-in user, enabling Row-Level Security testing
4. Verify: Query `dim_student` to confirm the email was updated for `student_key = 1`

### Notebook 04: Ingest Public Holidays

1. Open `04_ingest_publicholidays`
2. Click **Run all**
3. Wait for completion (~1 minute)
4. Verify: Navigate to Lakehouse → **Tables** → confirm `dim_publicholidays` table exists (~70 rows)
5. This creates a standalone dimension with Singapore public holidays (2021–2026)

---

## Step 6: Create Semantic Model

Step-by-step instructions for creating the **university-analytics-model** Power BI semantic model on the Fabric Lakehouse Delta tables.

**Prerequisites:**
- Notebooks 01–04 completed: all 14 Delta tables exist in `university` database
- Power BI Desktop (optional, for advanced editing and RLS testing)

### 6a: Create the Semantic Model

1. Navigate to your **Lakehouse** in the Fabric workspace
2. Click **New semantic model** (top ribbon)
3. Name: `university-analytics-model`
4. Select all 14 tables from the `university` database:
   - dim_date, dim_department, dim_program, dim_staff, dim_course
   - bridge_course_program
   - dim_exam_type, dim_fee_type, dim_academic_period, dim_student
   - dim_publicholidays
   - fact_enrollments, fact_exam_results, fact_financial_transactions
5. Click **Create**

### 6b: Define Relationships

Switch to **Model view** and create 19 relationships.

All are **Many-to-One**, **Single** cross-filter direction.

| # | From Table | From Column | To Table | To Column |
|---|-----------|-------------|----------|-----------|
| 1 | fact_enrollments | student_key | dim_student | student_key |
| 2 | fact_enrollments | course_key | dim_course | course_key |
| 3 | fact_enrollments | academic_period_key | dim_academic_period | academic_period_key |
| 4 | fact_enrollments | program_key | dim_program | program_key |
| 5 | fact_enrollments | enroll_date_key | dim_date | date_key |
| 6 | fact_exam_results | student_key | dim_student | student_key |
| 7 | fact_exam_results | course_key | dim_course | course_key |
| 8 | fact_exam_results | exam_type_key | dim_exam_type | exam_type_key |
| 9 | fact_exam_results | academic_period_key | dim_academic_period | academic_period_key |
| 10 | fact_exam_results | staff_key | dim_staff | staff_key |
| 11 | fact_exam_results | exam_date_key | dim_date | date_key |
| 12 | fact_financial_transactions | student_key | dim_student | student_key |
| 13 | fact_financial_transactions | fee_type_key | dim_fee_type | fee_type_key |
| 14 | fact_financial_transactions | academic_period_key | dim_academic_period | academic_period_key |
| 15 | fact_financial_transactions | course_key | dim_course | course_key |
| 16 | fact_financial_transactions | transaction_date_key | dim_date | date_key |
| 17 | bridge_course_program | course_key | dim_course | course_key |
| 18 | bridge_course_program | program_key | dim_program | program_key |
| 19 | dim_course | department_key | dim_department | department_key |


> **Note:** Two dimension-to-dimension foreign keys are intentionally omitted as active relationships because they create ambiguous filter paths in Power BI:
>
> - **dim_staff.department_key → dim_department** — would create a second path from dim_department to fact_exam_results (via dim_staff), conflicting with the existing path via dim_course.
> - **dim_course.coordinator_staff_key → dim_staff** — would create a second path from dim_staff to fact_exam_results (via dim_course), conflicting with the direct staff_key relationship.
>
> Staff department context can be accessed using `LOOKUPVALUE(dim_department[department_name], dim_department[department_key], dim_staff[department_key])` or by creating a calculated column on dim_staff.

#### How to Create a Relationship

1. In Model view, drag from the source column to the target column
2. Or: right-click a table → **Manage relationships** → **New**
3. Set cardinality to **Many to One**
4. Set cross-filter direction to **Single**
5. Ensure **Make this relationship active** is checked

### 6c: Create DAX Measures

Create measures in the following display folders. To set a display folder, select the measure → Properties → Display folder.

#### Folder: Enrolment Analytics

```dax
Total Enrolments = COUNTROWS(fact_enrollments)

Active Enrolments =
CALCULATE(
    COUNTROWS(fact_enrollments),
    fact_enrollments[enrollment_status] = "Enrolled"
)

Unique Students = DISTINCTCOUNT(fact_enrollments[student_key])

Completion Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_enrollments),
        fact_enrollments[enrollment_status] = "Completed"
    ),
    COUNTROWS(fact_enrollments)
)

Withdrawal Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_enrollments),
        fact_enrollments[enrollment_status] = "Withdrawn"
    ),
    COUNTROWS(fact_enrollments)
)

Total MCs Earned = SUM(fact_enrollments[credit_points_earned])

Total MCs Attempted = SUM(fact_enrollments[credit_points_attempted])
```

#### Folder: Academic Performance

```dax
Average Score = AVERAGE(fact_exam_results[score_percentage])

Average GPA = AVERAGE(fact_exam_results[grade_points])

Pass Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_exam_results),
        fact_exam_results[grade_letter] <> "F"
    ),
    COUNTROWS(fact_exam_results)
)

Distinction Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_exam_results),
        fact_exam_results[grade_letter] IN {"A+", "A", "A-"}
    ),
    COUNTROWS(fact_exam_results)
)

Exam Count = COUNTROWS(fact_exam_results)

Average Weighted Score = AVERAGE(fact_exam_results[weighted_score])

Fail Count =
CALCULATE(
    COUNTROWS(fact_exam_results),
    fact_exam_results[grade_letter] = "F"
)

Students at Academic Risk =
CALCULATE(
    DISTINCTCOUNT(fact_enrollments[student_key]),
    FILTER(
        VALUES(fact_enrollments[student_key]),
        CALCULATE(AVERAGE(fact_enrollments[course_gpa_points])) < 2.0
    )
)

Course Difficulty Index = 1 - [Pass Rate]
```

#### Folder: Financial Analytics

```dax
Total Revenue =
CALCULATE(
    SUM(fact_financial_transactions[amount]),
    fact_financial_transactions[transaction_type] = "Charge"
)

Total Payments =
CALCULATE(
    SUM(fact_financial_transactions[amount]),
    fact_financial_transactions[transaction_type] = "Payment"
)

Outstanding Balance = [Total Revenue] - [Total Payments]

Total Scholarships =
CALCULATE(
    SUM(fact_financial_transactions[amount]),
    fact_financial_transactions[transaction_type] = "Credit"
)

Transaction Count = COUNTROWS(fact_financial_transactions)

Average Tuition =
CALCULATE(
    AVERAGE(fact_financial_transactions[amount]),
    fact_financial_transactions[transaction_type] = "Charge",
    dim_fee_type[fee_type_name] = "Tuition"
)

Overdue Amount =
CALCULATE(
    SUM(fact_financial_transactions[amount]),
    fact_financial_transactions[is_overdue] = TRUE()
)

Collection Rate = DIVIDE([Total Payments], [Total Revenue])

Students with Overdue Balance =
CALCULATE(
    DISTINCTCOUNT(fact_financial_transactions[student_key]),
    fact_financial_transactions[is_overdue] = TRUE()
)
```

#### Folder: Per-Student Metrics

```dax
Revenue Per Student = DIVIDE([Total Revenue], [Unique Students])

MCs Per Student = DIVIDE([Total MCs Earned], [Unique Students])

GPA Per Student =
AVERAGEX(
    VALUES(dim_student[student_key]),
    CALCULATE(AVERAGE(fact_exam_results[grade_points]))
)

Avg Exams Per Student = DIVIDE([Exam Count], [Unique Students])

Avg Courses Per Student = DIVIDE([Total Enrolments], [Unique Students])

Payment Rate = DIVIDE([Total Payments], [Total Revenue])

Scholarship Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(dim_student),
        dim_student[scholarship_flag] = TRUE()
    ),
    COUNTROWS(dim_student)
)
```

### 6d: Create Hierarchies

#### Academic Calendar (on dim_academic_period)
1. Right-click `academic_year` → **Create hierarchy**
2. Name: `Academic Calendar`
3. Add levels: `academic_year` → `semester`

#### Academic Structure (on dim_department)
1. Right-click `faculty` → **Create hierarchy**
2. Name: `Academic Structure`
3. Add levels: `faculty` → `department_name`

#### Course Hierarchy (on dim_course)
1. Right-click `level` → **Create hierarchy**
2. Name: `Course Hierarchy`
3. Add levels: `level` → `course_name`

#### Fee Hierarchy (on dim_fee_type)
1. Right-click `fee_category` → **Create hierarchy**
2. Name: `Fee Hierarchy`
3. Add levels: `fee_category` → `fee_type_name`

### 6e: Configure Row-Level Security (RLS)

#### Staff Role
1. Go to **Modeling** → **Manage roles**
2. Click **New** → Name: `Staff`
3. **No DAX filter** — staff see all data
4. Click **Save**

#### Student Role
1. Click **New** → Name: `Student`
2. Select `dim_student` table
3. Add DAX filter:
   ```dax
   [email] = USERPRINCIPALNAME()
   ```
4. Click **Save**

#### Assign Members
1. In the Fabric workspace, find the semantic model
2. Click **Security** → select role
3. Add Azure AD users/groups to the appropriate role

#### Test RLS
1. In Power BI Desktop: **Modeling** → **View as** → select `Student` role
2. Enter test email: `stu0042@e.university.edu.sg`
3. Verify only that student's data appears
4. Test `Staff` role to confirm full access

### 6f: Semantic Model Validation

- [ ] All 14 tables visible in the semantic model
- [ ] All 19 relationships created (check Model view)
- [ ] No ambiguity warnings on relationships
- [ ] All DAX measures calculate correctly (test in a report visual)
- [ ] Hierarchies allow drill-down in visuals
- [ ] Staff role shows all data
- [ ] Student role filters to a single student
- [ ] Data Agents can access the model (test a simple prompt)


---

## Step 7: Create Ontology (Preview)

Follow the hands-on lab in [`05-ontology_lab.md`](05-ontology_lab.md).

---

## Step 8: Create Data Agents

Follow the hands-on lab in [`06-data_agent_lab.md`](06-data_agent_lab.md).

---

## Step 9: Pre-Demo Verification

Run through this checklist before presenting:

### Data Layer
- [ ] Lakehouse `university_lakehouse` exists
- [ ] 13 Parquet files under `Files/parquet/`
- [ ] 14 Delta tables under `Tables/` (13 from Notebook 02 + dim_publicholidays from Notebook 04)
- [ ] Row counts match expected values

### Semantic Model
- [ ] `university-analytics-model` model exists
- [ ] 19 relationships defined (no warnings)
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
