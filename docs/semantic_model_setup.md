# Semantic Model Setup Guide

Step-by-step instructions for creating the **university-analytics-model** Power BI semantic model on the Fabric Lakehouse Delta tables.

---

## Prerequisites

- Notebook 02 completed: all 13 Delta tables exist in `university` database
- Access to the Fabric workspace with Contributor or higher permissions
- Power BI Desktop (optional, for advanced editing and RLS testing)

---

## Step 1: Create the Semantic Model

1. Navigate to your **Lakehouse** in the Fabric workspace
2. Click **New semantic model** (top ribbon)
3. Name: `university-analytics-model`
4. Select all 13 tables from the `university` database:
   - dim_date, dim_department, dim_program, dim_staff, dim_course
   - bridge_course_program
   - dim_exam_type, dim_fee_type, dim_academic_period, dim_student
   - fact_enrollments, fact_exam_results, fact_financial_transactions
5. Click **Create**

---

## Step 2: Define Relationships

Switch to **Model view** and create 13 relationships.

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
| 11 | fact_financial_transactions | student_key | dim_student | student_key |
| 12 | fact_financial_transactions | fee_type_key | dim_fee_type | fee_type_key |
| 13 | fact_financial_transactions | academic_period_key | dim_academic_period | academic_period_key |

> **Note:** Dimension-to-dimension relationships (e.g., dim_course → dim_department, dim_student → dim_program) are intentionally omitted. They create ambiguous filter paths in Power BI when multiple dimensions share the same lookup table. Department and program context is available through denormalised columns (e.g., `dim_program[faculty]`) and through fact table joins.

### How to Create a Relationship

1. In Model view, drag from the source column to the target column
2. Or: right-click a table → **Manage relationships** → **New**
3. Set cardinality to **Many to One**
4. Set cross-filter direction to **Single**
5. Ensure **Make this relationship active** is checked

---

## Step 3: Create DAX Measures

Create measures in the following display folders. To set a display folder, select the measure → Properties → Display folder.

### Folder: Enrolment Analytics

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

### Folder: Academic Performance

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

### Folder: Financial Analytics

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

### Folder: Per-Student Metrics

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

---

## Step 4: Create Hierarchies

### Academic Calendar (on dim_academic_period)
1. Right-click `academic_year` → **Create hierarchy**
2. Name: `Academic Calendar`
3. Add levels: `academic_year` → `semester`

### Academic Structure (on dim_department)
1. Right-click `faculty` → **Create hierarchy**
2. Name: `Academic Structure`
3. Add levels: `faculty` → `department_name`

### Course Hierarchy (on dim_course)
1. Right-click `level` → **Create hierarchy**
2. Name: `Course Hierarchy`
3. Add levels: `level` → `course_name`

### Fee Hierarchy (on dim_fee_type)
1. Right-click `fee_category` → **Create hierarchy**
2. Name: `Fee Hierarchy`
3. Add levels: `fee_category` → `fee_type_name`

---

## Step 5: Configure Row-Level Security (RLS)

### Staff Role
1. Go to **Modeling** → **Manage roles**
2. Click **New** → Name: `Staff`
3. **No DAX filter** — staff see all data
4. Click **Save**

### Student Role
1. Click **New** → Name: `Student`
2. Select `dim_student` table
3. Add DAX filter:
   ```dax
   [email] = USERPRINCIPALNAME()
   ```
4. Click **Save**

### Assign Members
1. In the Fabric workspace, find the semantic model
2. Click **Security** → select role
3. Add Azure AD users/groups to the appropriate role

### Test RLS
1. In Power BI Desktop: **Modeling** → **View as** → select `Student` role
2. Enter test email: `stu0042@e.university.edu.sg`
3. Verify only that student's data appears
4. Test `Staff` role to confirm full access

---

## Validation Checklist

- [ ] All 13 tables visible in the semantic model
- [ ] All 13 relationships created (check Model view)
- [ ] No ambiguity warnings on relationships
- [ ] All DAX measures calculate correctly (test in a report visual)
- [ ] Hierarchies allow drill-down in visuals
- [ ] Staff role shows all data
- [ ] Student role filters to a single student
- [ ] Data Agents can access the model (test a simple prompt)
