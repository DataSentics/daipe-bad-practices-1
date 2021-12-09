# Databricks notebook source
# MAGIC %run ../../../../app/bootstrap

from pyspark.sql.dataframe import DataFrame
from datalakebundle.imports import transformation, table_append, read_delta
from daipeproject.silver.custom_attrs.schema import get_schema

# COMMAND ----------

@transformation(read_delta("%paths.raw.custom_attrs%/*"))
@table_append("ga_db.custom_attrs", get_schema())
def process_custom_attrs(df: DataFrame):
    return df
