# Fabric IQ Education Demo — Presenter Guide

## Overview

A two-notebook Microsoft Fabric demo for university customers showcasing the full data-to-insight pipeline: star-schema data model, Lakehouse Delta tables, Power BI semantic model, Fabric IQ Ontology, and Data Agent experiences for Staff and Student personas.

**Duration:** ~45 minutes (adjustable)
**Audience:** University IT leaders, data teams, academic administrators
**Fabric SKU:** F64 or higher (required for AI features)

---

## Pre-Demo Checklist

- [ ] Fabric workspace created with F64+ capacity
- [ ] Lakehouse `university_lakehouse` created
- [ ] All 2 notebooks uploaded to workspace
- [ ] Notebook 01 executed successfully (data generated)
- [ ] Notebook 02 executed successfully (13 Delta tables created)
- [ ] Semantic model `university-analytics-model` created and configured
- [ ] All 13 relationships defined
- [ ] All DAX measures created
- [ ] RLS roles configured (Staff + Student)
- [ ] Power BI report created with key visuals
- [ ] Staff Data Agent created and tested
- [ ] Student Data Agent created and tested
- [ ] Ontology `university-ontology` created with entity types and relationships
- [ ] Ontology graph refreshed and preview experience tested
- [ ] Test run all 4 NL queries in ontology
- [ ] Browser tabs pre-loaded: Lakehouse, Notebooks, Report, Data Agents

---

## Demo Flow

### Opening (3 min)

**Talking points:**
- "Today I want to show you how Microsoft Fabric can transform your university's data into actionable insights — from raw student records all the way to natural language Q&A."
- "We'll walk through the complete journey: data generation, star-schema modelling, a Power BI semantic model, and then three AI-powered experiences — an IQ Ontology, and Data Agents for Staff and Student personas."
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

**Show:** Power BI Model view (see `docs/semantic_model_setup.md` for configuration steps)

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

### Act 3: Fabric IQ Ontology (10 min)

**Show:** Ontology preview experience in Fabric portal

**Talking points:**
- "Now let's look at a newer Fabric capability: the IQ Ontology. It lets you define business concepts — like Student, Course, Program — as entity types, with typed properties and explicit relationships."
- "Unlike a semantic model which is optimised for Power BI reporting, an ontology creates a shared vocabulary that any tool — Data Agents, notebooks, applications — can use."
- "The ontology binds directly to our Delta tables. No data copying."

**Demo Scene 1:** Open the Student entity type overview, then query: *"Show me a summary of student enrolments by program and semester for the last 2 academic years"*
- "Notice the ontology traverses relationships — Student → Course → Program → AcademicPeriod — automatically."

**Demo Scene 2:** Query: *"Compare the average exam scores between domestic and international students across all departments"*
- "It uses the `examined_in` relationship and the Student property `domestic_international` — business terms, not table columns."

**Demo Scene 3:** Query: *"What is the outstanding balance by program, and which programs have the highest overdue amounts?"*
- "Financial data aggregated by following `pays_for` and `studies_program` relationships."

**Demo Scene 4:** Query: *"Show me students who have failed more than 2 courses and their current enrolment status"*
- "This is cross-domain reasoning — combining enrolment outcomes with student status in one query."

**Transition:** "The ontology gives us a governed business vocabulary. Now let's see purpose-built Data Agent experiences for specific user roles."

---

### Act 4: Data Agent — Staff Persona (8 min)

**Show:** Fabric Data Agent interface (Staff persona)

**Talking points:**
- "Data Agents are conversational AI assistants connected to your semantic model. Think of them as specialised chatbots for your data."
- "This agent is configured for university staff — full access, no row filters."

**Demo 3-4 questions from the staff test questions in `docs/fabric_setup_guide.md`:**
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

**Show:** Fabric Data Agent interface (Student persona)

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
  4. An IQ Ontology with entity types, relationships, and natural language queries
  5. Role-based Data Agents for staff and students
- "The key insight: **a well-structured data foundation powers every AI experience.** The semantic model drives reporting, the ontology provides a shared business vocabulary, and Data Agents deliver role-based conversational analytics."
- "This entire demo can be replicated in your environment. We'll share the notebooks and documentation."

**Questions:** Open for Q&A

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Ontology not available | Enable Ontology (preview) and Graph (preview) in tenant admin settings |
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
