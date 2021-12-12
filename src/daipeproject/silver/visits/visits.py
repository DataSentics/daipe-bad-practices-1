# Databricks notebook source
# MAGIC %run ../../app/bootstrap

# COMMAND ----------

from pyspark.sql.dataframe import DataFrame
from datalakebundle.imports import transformation, table_overwrite, read_csv, read_table
import pyspark.sql.functions as f
import pyspark.sql.types as t

from daipeproject.bronze.visits.schema import get_schema as get_csv_schema
from daipeproject.silver.visits.schema import get_schema as get_table_schema

# COMMAND ----------

def get_unique_custom_attrs(schema: t.StructType):
    return [field.name for field in schema.fields if "custom_field" in field.metadata and field.metadata["custom_field"] is True]
  
def get_mapping_col_name(name: str):
    return name + "_column"

# COMMAND ----------

@transformation("%datasets%", display=True)
def custom_attrs_mapping(datasets):
    unique_custom_attrs = get_unique_custom_attrs(get_table_schema())
    schema = ["name"] + [get_mapping_col_name(name) for name in unique_custom_attrs]
  
    data = []
    
    for dataset in datasets:
        row = tuple([dataset.name] + [dataset.custom_attrs[attr] if attr in dataset.custom_attrs else None for attr in unique_custom_attrs])
      
        data.append(row)
  
    return spark.createDataFrame(data, schema=schema)

# COMMAND ----------

@transformation(
    custom_attrs_mapping,
    read_csv(
        "%datalake.base_path%/bronze/raw/visits", # or "%datalake.base_path%/bronze/raw/visits/*" (without name as partition_key)
        schema=get_csv_schema(),
        options=dict(header='true')
    ),
    display=True
)
@table_overwrite("daipe_demo_ga_db.visits", get_table_schema(), recreate_table=True)
def process_visits(custom_attrs_mapping_df: DataFrame, df: DataFrame):    
    table_schema = get_table_schema()
    
    custom_x_cols = [field.name for field in df.schema.fields if field.name[:7] == "custom_"]
    
    def create_custom_column(custom_attr: str, custom_x_cols: list):
        mapping_col = get_mapping_col_name(custom_attr)
        conditions = [f.when(f.col(mapping_col) == custom_x_col, f.col(custom_x_col)) for custom_x_col in custom_x_cols]
        datatype = table_schema[custom_attr].dataType
        
        return f.coalesce(*conditions).cast(datatype).alias(custom_attr)
    
    select_columns = [
        f.col("name"),
        f.to_date(f.col("date"), 'yyyy-MM-dd').alias("date"),
        f.col("visits"),
    ] + [create_custom_column(custom_attr, custom_x_cols) for custom_attr in get_unique_custom_attrs(table_schema)]
    
    return (
        df
           .join(custom_attrs_mapping_df, on="name")
           .select(*select_columns)
           .sort(f.col("name"), f.col("date").asc())
    )
