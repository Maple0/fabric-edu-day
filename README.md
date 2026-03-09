# Fabric Education Demo

A two-notebook Microsoft Fabric demo for university customers showcasing the full data-to-insight pipeline: star-schema data model, Lakehouse Delta tables, Power BI semantic model, Fabric IQ Ontology, and Data Agent experiences for Staff and Student personas.


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
│   └── 02_star_schema_delta_tables        # Delta tables + DQ checks
│
└── docs/
    ├── 01-architecture_diagram.md            # Mermaid + ASCII diagrams
    ├── 02-data_dictionary.md                 # All tables + columns
    ├── 03-demo_guide.md                      # Presenter script (~45 min)
    ├── 04-fabric_setup_guide.md              # Environment setup + semantic model
    ├── 05-ontology_lab.md                    # Hands-on lab: Fabric IQ Ontology
    └── 06-data_agent_lab.md                  # Hands-on lab: Data Agents
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

**Execution order:** 01 → 02 (sequential). Semantic model, ontology, and Data Agent setup is documented in `docs/04-fabric_setup_guide.md`.

## Requirements

- **Fabric capacity:** F8 or higher (required for AI features)
- **Runtime:** Fabric Runtime 1.3 (PySpark)
- **Local:** Python 3.9+, packages in `requirements.txt`

## Documentation

- **[Demo Guide](docs/03-demo_guide.md)** — Full presenter script with talking points
- **[Data Dictionary](docs/02-data_dictionary.md)** — All tables, columns, and business definitions
- **[Fabric Setup Guide](docs/04-fabric_setup_guide.md)** — Environment setup + semantic model
- **[Architecture Diagram](docs/01-architecture_diagram.md)** — Mermaid and ASCII diagrams
- **[Ontology Lab](docs/05-ontology_lab.md)** — Hands-on lab for Fabric IQ Ontology
- **[Data Agent Lab](docs/06-data_agent_lab.md)** — Hands-on lab for Data Agents

## Key Highlights

- **520 students** across 12 programs and 8 departments
- **NUS 5.0 GPA scale** (A+/A/A-/B+/B/B-/C+/C/D+/D/F, 11 grade levels)
- **Bimodal score distribution** (8% fail cluster + 92% pass cluster)
- **70/30 domestic/international split** with realistic fee structures (SGD)
- **Row-Level Security** — students see only their own data
- **Singapore university context** — SGD currency, NUS grading, Aug-start academic calendar
