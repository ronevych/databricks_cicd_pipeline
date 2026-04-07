import sys
import dlt
from pyspark.sql.functions import *
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
path = spark.conf.get("spark.env.PYTHONPATH", "")

if path and path not in sys.path:
    sys.path.append(path)

from utilities.data_contracts import VIDEO_GAMES_SCHEMA, EXPECTATIONS

data_path = "/Volumes/dbr_dev/ronevych_raw/videogames_volume/"

@dlt.table(
    name = "video_games_bronze_bundle", 
    schema = "bronze", 
    comment = "Raw video games data"
)
@dlt.expect_all_or_drop(EXPECTATIONS)
def video_games_bronze():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("header", "true")
            .schema(VIDEO_GAMES_SCHEMA)
            .load(data_path) 
            .select(
                "*", 
                col("_metadata.file_path").alias("_source_filename"), 
                current_timestamp().alias("_ingestion_timestamp")
            )
    )