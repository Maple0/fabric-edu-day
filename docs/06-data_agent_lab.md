# Hands-On Lab: Data Agents

Create two Fabric Data Agents — a Staff persona with full access and a Student persona scoped by Row-Level Security — connected to the university semantic model.

---

## Prerequisites

- Semantic model `university-analytics-model` created and configured (see Step 6 in [`04-fabric_setup_guide.md`](04-fabric_setup_guide.md))
- RLS roles configured: Staff (full access) and Student (email filter on dim_student)
- Data Agents enabled in Fabric tenant admin settings

---

## Step 1: Create Staff Agent

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

student enrollments status contains "Withdrawn","Graduated","Suspended","Active"

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

---

## Step 2: Create Student Agent

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

---

## Step 3: Verify RLS

> **RLS verification:** Ask *"show me all students' GPAs"* — the agent should respond that it only has access to this student's records. If it returns data for multiple students, the RLS role is not configured correctly.

---

## Validation Checklist

- [ ] Staff Data Agent answers all 10 test questions correctly
- [ ] Student Data Agent scoped to a single student's data
- [ ] RLS verification confirms data isolation
