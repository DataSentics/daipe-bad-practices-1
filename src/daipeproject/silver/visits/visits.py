# Databricks notebook source
# MAGIC %run ../../../../app/bootstrap

from pyspark.sql.dataframe import DataFrame
from datalakebundle.imports import transformation, table_append, read_delta
from daipeproject.silver.visits.schema import get_schema

# COMMAND ----------

@transformation(read_delta("%datalake.base_path%/bronze/raw/visits/*"))
@table_append("ga_db.visits", get_schema()) # Note: přidal jsem schéma
def process_visits(df: DataFrame):
    return df
