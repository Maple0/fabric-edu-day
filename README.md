# Fabric IQ Education Demo

A six-notebook Microsoft Fabric demo for university customers showcasing the full data-to-insight pipeline: star-schema data model, Lakehouse Delta tables, Power BI semantic model, Fabric IQ Copilot insights, and Data Agent experiences for Staff and Student personas.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sample data (local)
python scripts/generate_data.py --format both --output-dir data

# 3. Validate data integrity
python scripts/validate_data.py --data-dir data

# 4. Upload notebooks to Microsoft Fabric and follow the demo guide
```

## Project Structure

```
edu-fabric-iq/
├── README.md                              # This file
├── .gitignore
├── requirements.txt                       # faker, pandas, pyarrow, numpy, scipy
│
├── scripts/
│   ├── config.py                          # Centralised CONFIG dict
│   ├── generate_data.py                   # All 13 table generators
│   ├── validate_data.py                   # FK + null + range checks
│   └── data_quality_checks.py             # Reusable assertion functions
│
├── data/
│   ├── raw/                               # 13 CSV files (human-readable)
│   └── parquet/                           # 13 Parquet files (Fabric upload)
│
├── notebooks/
│   ├── 01_data_generation_and_ingestion   # PySpark data gen → Lakehouse
│   ├── 02_star_schema_delta_tables        # Delta tables + DQ checks
│   ├── 03_semantic_model_configuration    # Relationships, DAX, RLS
│   ├── 04_fabric_iq_copilot_demo          # 4 Copilot demo scenes
│   ├── 05_data_agent_staff_persona        # 10 staff NL questions
│   └── 06_data_agent_student_persona      # 10 student NL questions
│
└── docs/
    ├── demo_guide.md                      # Presenter script (~45 min)
    ├── data_dictionary.md                 # All tables + columns
    ├── semantic_model_setup.md            # Step-by-step model setup
    ├── fabric_setup_guide.md              # Environment setup
    └── architecture_diagram.md            # Mermaid + ASCII diagrams
```

## Data Model

A star schema with 7 dimension tables, 1 bridge table, and 3 fact tables:

| Table | Type | Rows |
|-------|------|------|
| dim_date | Dimension | ~3,300 |
| dim_department | Dimension | 8 |
| dim_program | Dimension | 12 |
| dim_staff | Dimension | 80 |
| dim_course | Dimension | 60 |
| bridge_course_program | Bridge | ~380 |
| dim_exam_type | Dimension | 7 |
| dim_fee_type | Dimension | 8 |
| dim_academic_period | Dimension | 8 |
| dim_student | Dimension | 520 |
| fact_enrollments | Fact | ~10,900 |
| fact_exam_results | Fact | ~72,000 |
| fact_financial_transactions | Fact | ~7,500 |

## Notebooks

| # | Notebook | Purpose |
|---|----------|---------|
| 01 | Data Generation & Ingestion | Generate 13 tables with PySpark, write to Lakehouse |
| 02 | Star Schema Delta Tables | Explicit schemas, DQ assertions, managed Delta tables |
| 03 | Semantic Model Configuration | Relationships, DAX measures, hierarchies, RLS |
| 04 | Fabric IQ Copilot Demo | 4 scripted Copilot scenes with verification queries |
| 05 | Data Agent — Staff | 10 NL questions with full data access |
| 06 | Data Agent — Student | 10 NL questions scoped by RLS to one student |

**Execution order:** 01 → 02 → 03 (sequential), then 04/05/06 (independent).

## Requirements

- **Fabric capacity:** F64 or higher (required for Copilot)
- **Runtime:** Fabric Runtime 1.3 (PySpark)
- **Local:** Python 3.9+, packages in `requirements.txt`

## Documentation

- **[Demo Guide](docs/demo_guide.md)** — Full presenter script with talking points
- **[Data Dictionary](docs/data_dictionary.md)** — All tables, columns, and business definitions
- **[Semantic Model Setup](docs/semantic_model_setup.md)** — Relationships, DAX measures, RLS
- **[Fabric Setup Guide](docs/fabric_setup_guide.md)** — Environment setup checklist
- **[Architecture Diagram](docs/architecture_diagram.md)** — Mermaid and ASCII diagrams

## Key Highlights

- **520 students** across 12 programs and 8 departments
- **NUS 5.0 GPA scale** (A+/A/A-/B+/B/B-/C+/C/D+/D/F, 11 grade levels)
- **Bimodal score distribution** (8% fail cluster + 92% pass cluster)
- **70/30 domestic/international split** with realistic fee structures (SGD)
- **Row-Level Security** — students see only their own data
- **Singapore university context** — SGD currency, NUS grading, Aug-start academic calendar
