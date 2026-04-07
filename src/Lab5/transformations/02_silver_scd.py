import sys
import dlt
from pyspark.sql.functions import *
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
path = spark.conf.get("spark.env.PYTHONPATH", "")
if path and path not in sys.path:
    sys.path.append(path)
    
from utilities.data_contracts import SILVER_EXPECTATIONS

@dlt.view(name="video_games_bronze_clean_bundle")
@dlt.expect_all_or_drop(SILVER_EXPECTATIONS)
def video_games_bronze_clean():
    return (
        dlt.read_stream("bronze.video_games_bronze_bundle") 
            .select(
                col("Rank").alias("game_rank"),
                trim(col("Name")).alias("game_name"),
                col("Platform").alias("platform"),
                col("Year").alias("release_year"),
                col("Genre").alias("genre"),
                coalesce(col("Publisher"), lit("Unknown")).alias("publisher"),
                col("NA_Sales").alias("sales_na"),
                col("EU_Sales").alias("sales_eu"),
                col("JP_Sales").alias("sales_jp"),
                col("Other_Sales").alias("sales_other"),
                col("Global_Sales").alias("sales_global"),
                col("_source_filename").alias("_source_file"),
                col("_ingestion_timestamp")
            )
    )

dlt.create_streaming_table(
    name="silver.video_games_silver_scd_bundle", 
    comment="Full history of games (SCD2)"
)

dlt.apply_changes(
    target="silver.video_games_silver_scd_bundle",
    source="video_games_bronze_clean_bundle", 
    keys=["game_rank"],                
    sequence_by=col("_ingestion_timestamp"),
    track_history_column_list=["sales_global", "sales_na", "sales_eu"], 
    stored_as_scd_type=2
)