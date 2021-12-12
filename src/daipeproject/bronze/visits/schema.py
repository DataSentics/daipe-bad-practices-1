from pyspark.sql import types as t

def get_schema():
    return t.StructType(
        [
            t.StructField("name", t.StringType(), False),
            t.StructField("date", t.StringType(), False),
            t.StructField("visits", t.IntegerType(), False),
            t.StructField("custom_1", t.StringType(), True),
            t.StructField("custom_2", t.StringType(), True),
            t.StructField("custom_3", t.StringType(), True),
            t.StructField("custom_4", t.StringType(), True),
        ],
    )
