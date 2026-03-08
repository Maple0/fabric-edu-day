# Architecture Diagram — Fabric IQ Education Demo

## High-Level Architecture

```mermaid
graph LR
    subgraph "Data Generation"
        A[Python/Faker<br>generate_data.py] --> B[CSV Files]
        A --> C[Parquet Files]
    end

    subgraph "Microsoft Fabric Lakehouse"
        C --> D[Files/parquet/]
        D --> E[Delta Tables<br>13 managed tables]
    end

    subgraph "Semantic Layer"
        E --> F[Power BI<br>Semantic Model<br>'university-analytics-model']
        F --> G[13 Relationships]
        F --> H[30+ DAX Measures]
        F --> I[RLS Roles]
    end

    subgraph "AI Experiences"
        F --> J[Fabric IQ<br>Ontology]
        F --> K[Data Agent<br>Staff Persona]
        F --> L[Data Agent<br>Student Persona]
    end

    style A fill:#4CAF50,color:#fff
    style E fill:#2196F3,color:#fff
    style F fill:#FF9800,color:#fff
    style J fill:#9C27B0,color:#fff
    style K fill:#9C27B0,color:#fff
    style L fill:#9C27B0,color:#fff
```

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                        DATA GENERATION                               │
│                                                                      │
│  Python + Faker ──► 13 Tables (CSV + Parquet)                       │
│  (Local or Notebook 01)                                              │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     FABRIC LAKEHOUSE                                 │
│                                                                      │
│  Files/parquet/  ──► Notebook 02 ──► Delta Tables (university.*)    │
│                      (explicit schemas,    (OPTIMIZE + ZORDER)       │
│                       DQ assertions)                                 │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    SEMANTIC MODEL                                    │
│                                                                      │
│  university-analytics-model (Power BI on Fabric)                    │
│  ├── 13 Relationships (M:1, star schema)                            │
│  ├── 30+ DAX Measures (4 folders)                                   │
│  ├── 4 Hierarchies                                                   │
│  └── RLS: Staff (full) / Student (email filter)                     │
└──────────┬──────────────────┬────────────────────┬───────────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│  Fabric IQ      │ │  Data Agent     │ │  Data Agent          │
│  Ontology       │ │  Staff Persona  │ │  Student Persona     │
│                 │ │                 │ │                       │
│  4 NL queries   │ │  10 NL queries  │ │  10 NL queries       │
│  Graph preview  │ │  Full access    │ │  RLS-scoped          │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
```

## Star Schema — Entity Relationship Diagram

```mermaid
erDiagram
    dim_student ||--o{ fact_enrollments : "student_key"
    dim_student ||--o{ fact_exam_results : "student_key"
    dim_student ||--o{ fact_financial_transactions : "student_key"

    dim_course ||--o{ fact_enrollments : "course_key"
    dim_course ||--o{ fact_exam_results : "course_key"

    dim_exam_type ||--o{ fact_exam_results : "exam_type_key"
    dim_fee_type ||--o{ fact_financial_transactions : "fee_type_key"
    dim_staff ||--o{ fact_exam_results : "staff_key"

    dim_academic_period ||--o{ fact_enrollments : "academic_period_key"
    dim_academic_period ||--o{ fact_exam_results : "academic_period_key"
    dim_academic_period ||--o{ fact_financial_transactions : "academic_period_key"

    dim_program ||--o{ fact_enrollments : "program_key"

    dim_date ||--o{ fact_enrollments : "enroll_date_key"
    dim_date ||--o{ fact_exam_results : "exam_date_key"
    dim_date ||--o{ fact_financial_transactions : "transaction_date_key"

    dim_course ||--o{ bridge_course_program : "course_key"
    dim_program ||--o{ bridge_course_program : "program_key"
```

## Star Schema — ASCII View

```
                            ┌──────────────┐
                            │  dim_date    │
                            │  (calendar)  │
                            └──────┬───────┘
                                   │
        ┌──────────────┐    ┌──────┴───────┐    ┌──────────────────┐
        │  dim_staff   │    │              │    │  dim_exam_type   │
        │              ├────┤  fact_exam   ├────┤                  │
        └──────┬───────┘    │  _results    │    └──────────────────┘
               │            │              │
               │            └──────┬───────┘
               │                   │
┌──────────────┴──┐         ┌──────┴───────┐    ┌──────────────────┐
│  dim_department │         │  dim_student ├────┤  dim_program     │
│                 │         │              │    │                  │
└────────┬────────┘         └──┬───────┬───┘    └────────┬─────────┘
         │                     │       │                 │
         │              ┌──────┴──┐ ┌──┴────────────┐    │
┌────────┴────────┐     │  fact_  │ │  fact_         │    │
│  dim_course     ├─────┤  enrol- │ │  financial_   │    │
│                 │     │  ments  │ │  transactions │    │
└────────┬────────┘     └─────────┘ └───────┬───────┘    │
         │                                  │            │
         │              ┌───────────────────┘            │
         │              │                                │
    ┌────┴──────────┐   │    ┌──────────────────┐       │
    │ bridge_course │   │    │  dim_fee_type    │       │
    │ _program      │   │    │                  │       │
    └───────────────┘   │    └──────────────────┘       │
                        │                                │
                  ┌─────┴──────────────┐                │
                  │ dim_academic_period │                │
                  │                    │                │
                  └────────────────────┘                │
```

## Notebook Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                      NOTEBOOK PIPELINE                          │
│                                                                  │
│  ┌──────────┐   ┌──────────┐                                  │
│  │ NB 01    │──►│ NB 02    │                                  │
│  │ Generate  │   │ Delta    │                                  │
│  │ & Ingest │   │ Tables   │                                  │
│  └──────────┘   └──────────┘                                  │
│                                                                  │
│  Sequential: 01 → 02 (must run in order)                        │
│  Semantic model, ontology, agents: see fabric_setup_guide.md    │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Generation | Python, Faker, NumPy, SciPy | Synthetic university data |
| Storage | Fabric Lakehouse, Delta Lake | ACID-compliant data store |
| Compute | PySpark (Fabric Runtime 1.3) | Data processing & transformation |
| Semantic | Power BI Semantic Model | Business logic, measures, security |
| AI — Ontology | Fabric IQ Ontology | Business vocabulary, entity types, NL queries |
| AI — Agents | Fabric Data Agents | Role-based conversational analytics |
| Security | Row-Level Security (RLS) | Student data isolation |
