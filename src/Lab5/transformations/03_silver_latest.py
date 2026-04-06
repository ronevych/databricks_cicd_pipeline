import sys
import dlt
from pyspark.sql.functions import col

path = "/Workspace/Users/dmytro874@softserve.academy/.bundle/ronevych_videogames/dev/files/src/Lab5"
if path not in sys.path:
    sys.path.append(path)
from utilities.data_contracts import SILVER_EXPECTATIONS

@dlt.table(
    name="video_games_silver_latest_bundle", 
    comment="Cleaned data without history"
)
@dlt.expect_all_or_drop(SILVER_EXPECTATIONS)
def video_games_silver_latest():
    return (
        dlt.read_stream("video_games_bronze_clean_bundle")
            .select("*")
            .dropDuplicates(["game_rank"]) 
    )