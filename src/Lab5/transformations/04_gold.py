import dlt
from pyspark.sql.functions import col, sum, count, avg, round, current_timestamp

# --- Dimensions ---

@dlt.table(
    name="gold.dim_game_bundle", 
    comment="Dimension: Unique games metadata"
)
def dim_game():
    return (
        dlt.read("silver.video_games_silver_latest_bundle") 
            .select(
                col("game_rank").alias("game_id"), 
                "game_name", 
                "release_year", 
                "genre"
            )
            .distinct()
    )

@dlt.table(
    name="gold.dim_publisher_bundle", 
    comment="Dimension: Unique publishers"
)
def dim_publisher():
    return (
        dlt.read("silver.video_games_silver_latest_bundle")
            .select("publisher")
            .distinct()
    )

# --- Fact Table ---

@dlt.table(
    name="gold.fact_sales_bundle",
    comment="Fact: Sales transactions per game/platform"
)
def fact_sales():
    return (
        dlt.read("silver.video_games_silver_latest_bundle") 
            .select(
                col("game_rank").alias("game_id"),
                "publisher",
                "platform",
                "sales_na",
                "sales_eu",
                "sales_jp",
                "sales_other",
                "sales_global",
                current_timestamp().alias("_load_timestamp")
            )
    )

# --- Aggregations ---

@dlt.table(
    name="gold.gold_publisher_performance_bundle"
)
def gold_publisher_performance():
    return (
        dlt.read("gold.fact_sales_bundle")
            .groupBy("publisher")
            .agg(
                round(sum("sales_global"), 2).alias("total_global_sales"),
                count("game_id").alias("total_games_released"),
                round(avg("sales_global"), 2).alias("avg_sales_per_game")
            )
    )

@dlt.table(
    name="gold.gold_genre_trends_bundle"
)
def gold_genre_trends():
    df_fact = dlt.read("gold.fact_sales_bundle")
    df_dim = dlt.read("gold.dim_game_bundle")
    
    return (
        df_fact.join(df_dim, "game_id")
            .groupBy("release_year", "genre")
            .agg(round(sum("sales_global"), 2).alias("yearly_global_sales"))
    )