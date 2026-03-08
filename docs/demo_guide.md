# Fabric IQ Education Demo — Presenter Guide

## Overview

A six-notebook Microsoft Fabric demo for university customers showcasing the full data-to-insight pipeline: star-schema data model, Lakehouse Delta tables, Power BI semantic model, Fabric IQ Copilot insights, and Data Agent experiences for Staff and Student personas.

**Duration:** ~45 minutes (adjustable)
**Audience:** University IT leaders, data teams, academic administrators
**Fabric SKU:** F64 or higher (required for Copilot features)

---

## Pre-Demo Checklist

- [ ] Fabric workspace created with F64+ capacity
- [ ] Lakehouse `university_lakehouse` created
- [ ] All 6 notebooks uploaded to workspace
- [ ] Notebook 01 executed successfully (data generated)
- [ ] Notebook 02 executed successfully (13 Delta tables created)
- [ ] Semantic model `university-analytics-model` created and configured
- [ ] All 13 relationships defined
- [ ] All DAX measures created
- [ ] RLS roles configured (Staff + Student)
- [ ] Power BI report created with key visuals
- [ ] Staff Data Agent created and tested
- [ ] Student Data Agent created and tested
- [ ] Copilot enabled in tenant settings
- [ ] Test run all 4 Copilot prompts
- [ ] Browser tabs pre-loaded: Lakehouse, Notebooks, Report, Data Agents

---

## Demo Flow

### Opening (3 min)

**Talking points:**
- "Today I want to show you how Microsoft Fabric can transform your university's data into actionable insights — from raw student records all the way to natural language Q&A."
- "We'll walk through the complete journey: data generation, star-schema modelling, a Power BI semantic model, and then two AI-powered experiences — Copilot and Data Agents."
- "Everything you see today runs on a single Fabric workspace. No separate infrastructure to manage."

---

### Act 1: The Data Foundation (8 min)

**Show:** Notebook 01 — Data Generation & Ingestion

**Talking points:**
- "We start with synthetic university data — 520 students, 60 courses, 12 programs across 8 departments."
- "The data follows a classic star schema: dimension tables for students, courses, staff, and time periods, with fact tables for enrolments, exam results, and financial transactions."
- "We generate approximately 70,000 total rows — enough to be realistic, small enough to run in minutes."
- Show the row count summary cell
- Navigate to the Lakehouse UI and show files under Files/raw/ and Files/parquet/

**Show:** Notebook 02 — Star Schema Delta Tables

**Talking points:**
- "Now we convert those Parquet files into managed Delta tables with explicit schemas."
- "Delta format gives us ACID transactions, schema enforcement, and time travel — critical for a production data platform."
- "We run data quality checks: primary key uniqueness, foreign key integrity, null checks — all pass."
- Show the SHOW TABLES output
- "13 tables, all managed by the Lakehouse. No external storage to worry about."

**Transition:** "Now that we have clean, validated data in Delta tables, let's build the analytics layer."

---

### Act 2: The Semantic Model (7 min)

**Show:** Notebook 03 — Semantic Model Configuration (reference), then switch to Power BI Model view

**Talking points:**
- "The semantic model is the bridge between raw data and business insight. It defines relationships, reusable measures, and security rules."
- Show the Model view with all 13 relationships
- "13 relationships connect our star schema. Fact tables point to dimensions. Filters flow from dimensions to facts."
- Click into a DAX measure
- "We have 30+ measures organised into folders: Enrolment Analytics, Academic Performance, Financial Analytics, and Per-Student Metrics."
- Show the RLS configuration
- "Row-Level Security ensures students only see their own data. The filter on dim_student cascades through all fact tables automatically."

**Transition:** "Now let's see what happens when we add AI to this well-structured model."

---

### Act 3: Fabric IQ Copilot (10 min)

**Show:** Power BI report with Copilot panel open

**Talking points:**
- "Copilot reads the semantic model metadata — table names, measure definitions, relationships — to understand your data."
- "It generates DAX queries, not SQL. This means it respects all your business logic and security rules."

**Demo Scene 1:** Type: *"Summarise student enrolment trends over the last 4 academic years"*
- Wait for response
- "Notice how Copilot identified the right dimension, aggregated correctly, and even spotted the trend."

**Demo Scene 2:** Type: *"What are the courses with the highest and lowest pass rates this year?"*
- "It's using our Pass Rate measure definition. The semantic model gives Copilot the business logic."

**Demo Scene 3:** Type: *"Show me a financial summary for Semester 1 2024"*
- "Financial data filtered to a specific period — charges, payments, outstanding balance — all from measure definitions."

**Demo Scene 4:** Type: *"Which students are showing signs of academic risk?"*
- "This is where it gets powerful. Copilot is surfacing actionable insights — students below a 2.0 GPA threshold on the NUS 5.0 scale."
- "In a real deployment, this could trigger early intervention workflows."

**Transition:** "Copilot is great for ad-hoc exploration. But what about purpose-built experiences for specific user roles?"

---

### Act 4: Data Agent — Staff Persona (8 min)

**Show:** Fabric Data Agent interface (Staff persona)

**Talking points:**
- "Data Agents are conversational AI assistants connected to your semantic model. Think of them as specialised chatbots for your data."
- "This agent is configured for university staff — full access, no row filters."

**Demo 3-4 questions from the 10 in Notebook 05:**
1. *"How many students are currently enrolled this semester vs same semester last year?"*
2. *"Which undergraduate program has the highest and lowest average GPA this semester?"*
3. *"Do scholarship recipients perform better academically than non-scholarship students?"*
4. *"What was total tuition revenue collected in Semester 1 2024, split by domestic/international?"*

**Talking points after each answer:**
- "Notice the agent provides specific numbers, comparisons, and context."
- "It uses Singapore academic terminology — NUS 5.0 GPA scale, SGD currency, Modular Credits — because we configured that in the system prompt."
- "Staff can ask these questions without knowing DAX, SQL, or how to build a report."

---

### Act 5: Data Agent — Student Persona (5 min)

**Show:** Fabric Data Agent interface (Student persona) or Notebook 06

**Talking points:**
- "Now the same technology, but for individual students. RLS automatically scopes everything to one person."
- "The student sees only their own grades, enrolments, and financial records."

**Demo 2-3 questions:**
1. *"What is my current GPA?"*
2. *"How much do I currently owe the university?"*
3. *"Am I on track to graduate on time?"*

**Key point:**
- "If I ask 'show me all students' GPAs', the agent correctly responds that it only has access to this student's records. RLS is enforced at the model layer."

---

### Closing (4 min)

**Talking points:**
- "Let's recap what we built today — all within a single Fabric workspace:"
  1. Synthetic data generation with PySpark
  2. Delta table creation with schema enforcement
  3. A semantic model with relationships, measures, and RLS
  4. AI-powered insights via Copilot
  5. Role-based Data Agents for staff and students
- "The key insight: **a well-structured semantic model is the foundation for every AI experience.** Copilot and Data Agents are only as good as your model."
- "This entire demo can be replicated in your environment. We'll share the notebooks and documentation."

**Questions:** Open for Q&A

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Copilot not responding | Verify F64+ capacity, check tenant admin Copilot settings |
| Data Agent returns wrong numbers | Re-run Notebook 02, verify Delta tables match semantic model |
| RLS not filtering | Check dim_student[email] filter, verify relationship cross-filter direction |
| Notebook fails to run | Ensure Lakehouse is attached, check Fabric Runtime version (1.3+) |
| Measures show blank | Verify all 13 relationships are created in Model view |
| "No data" in visuals | Run Notebook 01 + 02 again, refresh semantic model |

---

## Customisation Notes

- **Different institution:** Update `CONFIG` in Notebook 01 — change department names, program names, student count
- **Different country:** Change `faker_locale` in CONFIG, update grade boundaries to local scale
- **Larger dataset:** Increase `n_students` (tested up to 5,000 with no issues)
- **Additional dimensions:** Add new dimension tables in the generation script, update schemas in Notebook 02
