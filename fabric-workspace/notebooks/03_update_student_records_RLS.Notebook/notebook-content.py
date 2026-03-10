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

# MAGIC %%sql
# MAGIC 
# MAGIC UPDATE university.dim_student
# MAGIC SET email = 'ligen@microsoft.com'
# MAGIC WHERE student_key = 1;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
