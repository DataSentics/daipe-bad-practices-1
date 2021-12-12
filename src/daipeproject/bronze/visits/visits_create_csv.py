# Databricks notebook source
# MAGIC %run ../../app/bootstrap

# COMMAND ----------

from pyspark.sql.dataframe import DataFrame
from pyspark.dbutils import DBUtils
from datalakebundle.imports import transformation, table_append, csv_overwrite

# COMMAND ----------

@transformation("%datalake.base_path%/bronze/raw/visits")
def cleanup(path: str, dbutils: DBUtils):
    dbutils.fs.rm(path, True)

# COMMAND ----------

from daipeproject.bronze.visits.schema import get_schema

@transformation(display=True)
@csv_overwrite("dbfs:/daipe-bad-practices/bronze/raw/visits", partition_by=["name"], options={"header": 'true'})
def store_raw_visits():  
    df = spark.createDataFrame(
        data=[
            ("knihydobrovsky_cz", "2021-01-01", 123, 465, 123, 999, None),
            ("knihydobrovsky_cz", "2021-01-02", 158, 465, 15, 0, None),
            ("knihomol_cz", "2021-01-01", 456, 987, 12, None, None),
            ("knihomol_cz", "2021-01-02", 879, 987, 12, None, None),
        ],
        schema=get_schema()
    )
    
    return df.coalesce(1)

# COMMAND ----------

dbutils.fs.ls("dbfs:/daipe-bad-practices/bronze/raw/visits/name=knihomol_cz")
