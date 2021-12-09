from datalakebundle.table.schema.TableSchema import TableSchema
from pyspark.sql import types as t

def get_schema():
    return TableSchema(
        [
            t.StructField("date", t.DateType(), True),
        ],
        primary_key=["session_id"],
        # partition_by = "Date" #---takes a very long time
    )
