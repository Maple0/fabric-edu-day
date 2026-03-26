# Hands-On Lab: Power BI Copilot

Use Power BI Copilot to create a report page and ask natural language questions against the university semantic model.

---

## Prerequisites

- Semantic model `university-analytics-model` created and configured (see Step 6 in [`04-fabric_setup_guide.md`](04-fabric_setup_guide.md))
- Power BI Copilot enabled in Fabric tenant admin settings (**Copilot and Azure OpenAI Service** toggle)

---

## Part 1: Create a Report Page with Copilot

Use Copilot to generate a new report page that analyses student performance metrics and trends.

### Step 1: Create a New Report from the Semantic Model

1. In your Fabric workspace, open the `university-analytics-model` semantic model
2. Click **Explore** → **Create a new blank report**
3. A new blank report opens in editing mode, already connected to the semantic model

### Step 2: Generate a Report Page with Copilot

1. Click the **Copilot** button in the ribbon to open the Copilot pane
2. Enter the following prompt:

   > *"Create a page to analyze student performance metrics and trends."*

3. Review the generated page — Copilot should create visuals using data from student, course, and enrolment tables
4. Click **Keep it** to accept the generated page, or **Undo** to try a different prompt

### Step 3: Save the Report

1. Click **File** → **Save**
2. Name the report (e.g., `University Student Performance Report`)
3. Save it to the same workspace

---

## Part 2: Ask Questions About Student Performance

Use Copilot to ask natural language questions about student performance in enrolled courses.

### Step 4: Ask About Overall Performance

1. With the Copilot pane open, enter:

   > *"What is the average GPA across all students for the 2026 academic year?"*

2. Review the response — Copilot should query `fact_enrollments` using `course_gpa_points` filtered to completed enrolments in academic year 2026

### Step 5: Analyse Failure Rates by Course

1. Enter:

   > *"display the number of students enrolled in different course for current academic year"*


---

## Validation Checklist

- [ ] Report created from the semantic model via **Explore** → **Create a new blank report**
- [ ] Copilot generated a report page with student performance visuals
- [ ] Copilot answers GPA question with correct data from the 2024 academic year
- [ ] Copilot returns top 5 courses by failure rate with course name, department, and percentage
