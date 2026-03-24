# Hands-On Lab: KQL Database & fact_attendance Table

Create a KQL database inside a Fabric Eventhouse and populate the `fact_attendance` table with daily attendance data derived from enrolment records.

---

## Prerequisites

- Fabric workspace with a Microsoft Fabric-enabled capacity
- Lakehouse `university_lakehouse` with `fact_enrollments` and `dim_publicholidays` tables already loaded (see [`04-fabric_setup_guide.md`](04-fabric_setup_guide.md))
- Shortcuts or external tables configured so the KQL database can query `fact_enrollments` and `dim_publicholidays`

---

## Step 1: Create the Eventhouse

1. In your Fabric workspace, click **New** → **Eventhouse**
2. Name: `university_eventhouse`
3. Click **Create**

> A default KQL database with the same name is created automatically inside the eventhouse.

---

## Step 2: Create the `fact_attendance` Table

1. Open the `university_eventhouse` KQL database
2. Click **Explore your data** (or open a new KQL queryset)
3. Run the following command to create the table:

```kql
.create table fact_attendance (
    student_key: int,
    course_key: int,
    date_key: int,
    is_present: bool,
    timestamp: datetime
)
```

### Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `student_key` | `int` | Foreign key to `dim_student` |
| `course_key` | `int` | Foreign key to `dim_course` |
| `date_key` | `int` | Date in `yyyyMMdd` format (e.g. `20260324`) |
| `is_present` | `bool` | `true` if the student attended, `false` if absent |
| `timestamp` | `datetime` | UTC timestamp of when the record was generated |

---

## Step 3: Create External Table Shortcuts

Before running the load query you need OneLake shortcuts so the KQL database can read from the lakehouse.

1. In the KQL database, click **New** → **OneLake shortcut**
2. Create shortcuts to the following lakehouse tables:
   - `fact_enrollments`
   - `dim_publicholidays`
3. Verify the external tables are accessible:

```kql
external_table("fact_enrollments") | take 5
```

```kql
external_table("dim_publicholidays") | take 5
```

---

## Step 4: Load Daily Attendance Data

Run the following KQL query to generate and load attendance records for today. This query:

1. Deletes any existing records for today (idempotent reload)
2. Derives attendance from completed enrolments
3. Randomly assigns ~95% of students as present
4. Skips weekends and public holidays

```kql
// Step 4a — Delete today's records (idempotent)
.delete table fact_attendance records <|
fact_attendance
| where date_key == toint(format_datetime(startofday(now()), 'yyyyMMdd'));

// Step 4b — Insert today's attendance
.set-or-append fact_attendance <|
external_table("fact_enrollments")
| where enrollment_status == "Completed"
| summarize by student_key, course_key
| extend date_key = toint(format_datetime(startofday(now()), 'yyyyMMdd'))
| extend is_present = iif(rand() < 0.95, true, false)
| extend timestamp = now()
| where dayofweek(now()) !in ("6.00:00:00", "00:00:00")
    and toscalar(
        external_table("dim_publicholidays")
        | where format_datetime(todatetime(holiday_key), 'yyyyMMdd') == format_datetime(startofday(now()), 'yyyyMMdd')
        | summarize count()
    ) == 0
| project student_key, course_key, date_key, is_present, timestamp
```

> **Note:** Run the delete and insert commands separately — the KQL query editor does not support multiple management commands in a single execution.

---

## Step 5: Verify the Data

```kql
fact_attendance
| where date_key == toint(format_datetime(startofday(now()), 'yyyyMMdd'))
| summarize TotalRecords = count(),
            PresentCount = countif(is_present == true),
            AbsentCount  = countif(is_present == false)
```

Expected result: roughly 95% present, 5% absent. If today is a weekend or public holiday the query in Step 4 will produce zero rows.

---

## Validation Checklist

- [ ] Eventhouse `university_eventhouse` created in the workspace
- [ ] KQL database contains the `fact_attendance` table with the correct schema
- [ ] External table shortcuts to `fact_enrollments` and `dim_publicholidays` working
- [ ] Daily attendance data loaded successfully for today's date
- [ ] Verification query returns expected present/absent split
