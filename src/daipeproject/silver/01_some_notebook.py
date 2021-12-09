# Databricks notebook source
# MAGIC %run ../../../../app/bootstrap

from pyspark.sql.dataframe import DataFrame
from datalakebundle.imports import transformation

# COMMAND ----------

datasets = [
    {
        "id": "123",
        "name": "knihydobrovsky_cz",
        "custom_attrs": {
            105: "EXT_ID",
            104: "ADFORM_ID",
            2: "GA_ID",
        },
    },
    {
        "id": "4564",
        "name": "knihomol_cz",
        "custom_attrs": {
            3: "EXT_ID",
            2: "GA_ID",
        },
    },
]

# TODO 2: tahání configu a předávání přes globální proměnnou
@transformation("%datalake.base_base_path%")
def get_config(base_base_path: str):
    return base_base_path

base_path = get_config.result

# TODO 1: cyklus
for dataset in datasets:
    # TODO 3: use logger instead of print
    print(dataset['name'])
    dataset_name = dataset['name']

    @transformation()
    def load_visits():
        return spark.read.format("delta").load(base_path + "/bronze/raw/visits/" + dataset_name)

    def load_custom_attrs():
        return spark.read.format("delta").load(base_path + "/bronze/raw/custom_attrs/" + dataset_name)

    # TODO 4: rule of thumb: one notebook should always produce/output one dataset
    @transformation(load_visits)
    def save_visits(df: DataFrame):
        df.write.format("delta").save(base_path + "/silver/parsed/visits/" + dataset_name, mode="append")

    @transformation(load_custom_attrs)
    def save_custom_attrs(df: DataFrame):
        df.write.format("delta").save(base_path + "/silver/parsed/custom_attrs/" + dataset_name, mode="append")
