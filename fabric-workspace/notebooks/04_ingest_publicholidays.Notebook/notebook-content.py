# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "dbcbadb4-fbbe-4751-9bab-ef25ff473bfb",
# META       "default_lakehouse_name": "university_lakehouse",
# META       "default_lakehouse_workspace_id": "7c9771e8-a91d-4115-b9ba-b39c0a3c79b1",
# META       "known_lakehouses": [
# META         {
# META           "id": "dbcbadb4-fbbe-4751-9bab-ef25ff473bfb"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************


from pyspark.sql import functions as F

holidays = [
     # ---- 2021 ----
    ("2021-01-01", "New Year's Day"),
    ("2021-02-12", "Chinese New Year"),
    ("2021-02-13", "Chinese New Year"),
    ("2021-04-02", "Good Friday"),
    ("2021-05-01", "Labour Day"),
    ("2021-05-13", "Hari Raya Puasa"),
    ("2021-05-26", "Vesak Day"),
    ("2021-07-20", "Hari Raya Haji"),
    ("2021-08-09", "National Day"),
    ("2021-11-04", "Deepavali"),
    ("2021-12-25", "Christmas Day"),

     # ---- 2022 ----
    ("2022-01-01", "New Year's Day"),
    ("2022-02-01", "Chinese New Year"),
    ("2022-02-02", "Chinese New Year"),
    ("2022-04-15", "Good Friday"),
    ("2022-05-01", "Labour Day"),
    ("2022-05-03", "Hari Raya Puasa"),
    ("2022-05-15", "Vesak Day"),
    ("2022-07-10", "Hari Raya Haji"),
    ("2022-08-09", "National Day"),
    ("2022-10-24", "Deepavali"),
    ("2022-12-25", "Christmas Day"),

    # ---- 2023 ----
    ("2023-01-01", "New Year's Day"),
    ("2023-01-22", "Chinese New Year"),
    ("2023-01-23", "Chinese New Year"),
    ("2023-04-07", "Good Friday"),
    ("2023-04-22", "Hari Raya Puasa"),
    ("2023-05-01", "Labour Day"),
    ("2023-06-02", "Vesak Day"),
    ("2023-06-29", "Hari Raya Haji"),
    ("2023-08-09", "National Day"),
    ("2023-09-01", "Polling Day"),
    ("2023-11-12", "Deepavali"),
    ("2023-12-25", "Christmas Day"),

    # ---- 2024 ---- 
    ("2024-01-01", "New Year's Day"),
    ("2024-02-10", "Chinese New Year"),
    ("2024-02-11", "Chinese New Year"),
    ("2024-03-29", "Good Friday"),
    ("2024-04-10", "Hari Raya Puasa"),
    ("2024-05-01", "Labour Day"),
    ("2024-05-22", "Vesak Day"),
    ("2024-06-17", "Hari Raya Haji"),
    ("2024-08-09", "National Day"),
    ("2024-10-31", "Deepavali"),
    ("2024-12-25", "Christmas Day"),

    # ---- 2025 ---- 
    ("2025-01-01", "New Year's Day"),
    ("2025-01-29", "Chinese New Year"),
    ("2025-01-30", "Chinese New Year"),
    ("2025-03-31", "Hari Raya Puasa"),
    ("2025-04-18", "Good Friday"),
    ("2025-05-01", "Labour Day"),
    ("2025-05-03", "Polling Day"),
    ("2025-05-12", "Vesak Day"),
    ("2025-06-07", "Hari Raya Haji"),
    ("2025-08-09", "National Day"),
    ("2025-10-20", "Deepavali"),
    ("2025-12-25", "Christmas Day"),

    # ---- 2026 ---- 
    ("2026-01-01", "New Year's Day"),
    ("2026-02-17", "Chinese New Year"),
    ("2026-02-18", "Chinese New Year"),
    ("2026-03-21", "Hari Raya Puasa"),
    ("2026-04-03", "Good Friday"),
    ("2026-05-01", "Labour Day"),
    ("2026-05-27", "Hari Raya Haji"),
    ("2026-05-31", "Vesak Day"),
    ("2026-08-09", "National Day"),
    ("2026-11-08", "Deepavali"),
    ("2026-12-25", "Christmas Day"),
]

base = (
    spark.createDataFrame(holidays, ["holiday_date_str", "holiday_name"])
    .withColumn("holiday_date", F.to_date("holiday_date_str"))
    .drop("holiday_date_str")
    .withColumn("country_code", F.lit("SG"))
    .withColumn("is_observed", F.lit(False))
    .withColumn("source", F.lit("MOM/data.gov.sg (2021–2026)"))  # datasets cited above [1](https://www.mssqltips.com/sqlservertip/7922/microsoft-fabric-eventstream-ingest-transform-route-data/)[2](https://www.linkedin.com/pulse/driving-rti-adoption-eventhouse-connectors-pablo-junco-boquer-hiy8e?tl=en)[3](https://www.youtube.com/watch?v=6QpURM97YXU)
)

# Spark dayofweek(): 1=Sunday, 2=Monday, ..., 7=Saturday
observed = (
    base
    .where(F.dayofweek("holiday_date") == 1)  # Sunday
    .withColumn("holiday_date", F.date_add("holiday_date", 1))   # Monday observed [4](https://github.com/MicrosoftDocs/fabric-docs/blob/main/docs/real-time-intelligence/spark-connector.md)
    .withColumn("holiday_name", F.concat(F.col("holiday_name"), F.lit(" (Observed)")))
    .withColumn("is_observed", F.lit(True))
)

publicholidays = base.unionByName(observed).dropDuplicates(["holiday_date", "holiday_name"])

# Add a numeric key YYYYMMDD
publicholidays = publicholidays.withColumn(
    "holiday_key",
    (F.year("holiday_date") * 10000 + F.month("holiday_date") * 100 + F.dayofmonth("holiday_date")).cast("int")
)

publicholidays.orderBy("holiday_date").show(50, truncate=False)

dim_publicholidays = publicholidays.select(
    "holiday_key",
    "holiday_date",
    "holiday_name",
    "is_observed",
    "source"
)

#dim_publicholidays



# Overwrite table with reordered columns
dim_publicholidays.write.mode("overwrite").format("delta").saveAsTable("university.dim_publicholidays")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
