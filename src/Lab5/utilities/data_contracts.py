import dlt
from pyspark.sql import types as T


VIDEO_GAMES_SCHEMA = T.StructType([
    T.StructField("Rank", T.IntegerType(), True),
    T.StructField("Name", T.StringType(), True),
    T.StructField("Platform", T.StringType(), True),
    T.StructField("Year", T.IntegerType(), True),
    T.StructField("Genre", T.StringType(), True),
    T.StructField("Publisher", T.StringType(), True),
    T.StructField("NA_Sales", T.DoubleType(), True),
    T.StructField("EU_Sales", T.DoubleType(), True),
    T.StructField("JP_Sales", T.DoubleType(), True),
    T.StructField("Other_Sales", T.DoubleType(), True),
    T.StructField("Global_Sales", T.DoubleType(), True)
])

EXPECTATIONS = {
    "valid_rank": "Rank IS NOT NULL",
    "valid_name": "Name IS NOT NULL",
    "positive_sales": "Global_Sales >= 0"
}

SILVER_EXPECTATIONS = {
    "game_rank_not_null": "game_rank IS NOT NULL",
    "sales_positive": "sales_global >= 0"
}