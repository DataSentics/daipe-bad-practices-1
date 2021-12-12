from datalakebundle.table.schema.TableSchema import TableSchema
from pyspark.sql import types as t

def get_schema():
    return TableSchema(
        [
            t.StructField("name", t.StringType(), False),
            t.StructField("date", t.DateType(), False),
            t.StructField("visits", t.IntegerType(), False),
            t.StructField("ga_id", t.IntegerType(), True, metadata={'custom_field': True}),
            t.StructField("ext_id", t.IntegerType(), True, metadata={'custom_field': True}),
            t.StructField("adform_id", t.IntegerType(), True, metadata={'custom_field': True}),
        ],
        primary_key=["name", "date"],
        partition_by=["name"]
    )
