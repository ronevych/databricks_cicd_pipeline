# Databricks notebook source
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

print(f"\n{'='*90}")
print(f"DATABRICKS UNITY CATALOG SECURITY POLICIES DEPLOYMENT")
print(f"{'='*90}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Catalog:   {catalog}")
print(f"Base Schema: {schema}")
print(f"{'='*90}\n")

# --- 1. SAFE DROP FUNCTIONS ---

def drop_row_filter_if_exists(layer_schema: str, table_name: str) -> None:
    full_table_name = f"{catalog}.{layer_schema}.{table_name}"
    try:
        spark.sql(f"ALTER TABLE {full_table_name} DROP ROW FILTER;")
        print(f"  ✓ Dropped existing ROW FILTER on {full_table_name}")
    except Exception:
        pass 

def drop_column_mask_if_exists(layer_schema: str, table_name: str, column_name: str) -> None:
    full_table_name = f"{catalog}.{layer_schema}.{table_name}"
    try:
        spark.sql(f"ALTER TABLE {full_table_name} ALTER COLUMN {column_name} DROP MASK;")
        print(f"  ✓ Dropped existing MASK on {full_table_name}.{column_name}")
    except Exception:
        pass 

def drop_function_if_exists(function_name: str) -> None:
    try:
        spark.sql(f"DROP FUNCTION IF EXISTS {function_name};")
    except Exception:
        pass

# --- 2. POLICY CREATION FUNCTIONS ---

def create_privileged_row_filter_function(function_name: str) -> None:
    drop_function_if_exists(function_name)
    spark.sql(f"""
    CREATE FUNCTION {function_name}()
    RETURNS BOOLEAN
    LANGUAGE SQL
    AS $$
        SELECT current_user() = 'lbiel@softserve.academy' 
               OR is_account_group_member('admins')
    $$;
    """)

def create_selective_row_filter_function(function_name: str) -> None:
    drop_function_if_exists(function_name)
    spark.sql(f"""
    CREATE FUNCTION {function_name}(game_id INT)
    RETURNS BOOLEAN
    LANGUAGE SQL
    AS $$
        SELECT CASE
            WHEN current_user() = 'lbiel@softserve.academy' 
                 OR is_account_group_member('admins') THEN TRUE
            WHEN game_id <= 10 THEN TRUE
            ELSE FALSE
        END
    $$;
    """)

def create_revenue_mask_function(function_name: str) -> None:
    drop_function_if_exists(function_name)
    spark.sql(f"""
    CREATE FUNCTION {function_name}(revenue_value DOUBLE)
    RETURNS DOUBLE
    LANGUAGE SQL
    AS $$
        SELECT CASE
            WHEN current_user() = 'lbiel@softserve.academy' 
                 OR is_account_group_member('admins') THEN revenue_value
            ELSE 0.0 
        END
    $$;
    """)

# --- 3. APPLY LAYER POLICIES ---

print(f"\n{'='*90}")
print("BRONZE & SILVER LAYERS - RESTRICTED DATA (ROW-LEVEL SECURITY)")
print(f"{'='*90}")

restricted_tables = [
    ("bronze", "video_games_bronze_bundle"),
    ("silver", "video_games_silver_scd_bundle"),
    ("silver", "video_games_silver_latest_bundle")
]

for layer_schema, table_name in restricted_tables:
    print(f"Processing: {catalog}.{layer_schema}.{table_name}")
    drop_row_filter_if_exists(layer_schema, table_name)
    
    filter_func = f"{catalog}.{layer_schema}.restricted_row_filter_{layer_schema}"
    create_privileged_row_filter_function(filter_func)
    
    spark.sql(f"ALTER TABLE {catalog}.{layer_schema}.{table_name} SET ROW FILTER {filter_func} ON ();")
    print(f"  ✓ Applied RLS to {table_name}\n")


print(f"\n{'='*90}")
print("GOLD DIMENSIONS - OPEN ACCESS")
print(f"{'='*90}")
for table_name in ["dim_game_bundle", "dim_publisher_bundle"]:
    print(f"✓ {catalog}.{schema}.{table_name} (No restrictions)")


print(f"\n{'='*90}")
print("GOLD FACT TABLE - RESTRICTED DATA (RLS + CLS)")
print(f"{'='*90}")

fact_table = "fact_sales_bundle"
print(f"Processing: {catalog}.{schema}.{fact_table}")

drop_row_filter_if_exists(schema, fact_table)
drop_column_mask_if_exists(schema, fact_table, "sales_global")

fact_filter_func = f"{catalog}.{schema}.fact_sales_row_filter"
create_selective_row_filter_function(fact_filter_func)
spark.sql(f"ALTER TABLE {catalog}.{schema}.{fact_table} SET ROW FILTER {fact_filter_func} ON (game_id);")

sales_mask_func = f"{catalog}.{schema}.mask_sales_global"
create_revenue_mask_function(sales_mask_func)
spark.sql(f"ALTER TABLE {catalog}.{schema}.{fact_table} ALTER COLUMN sales_global SET MASK {sales_mask_func};")
print("  ✓ Applied Top-10 RLS and Revenue CLS\n")


print(f"\n{'='*90}")
print("GOLD AGGREGATIONS - MASKED REVENUE COLUMNS (COLUMN-LEVEL SECURITY)")
print(f"{'='*90}")

pub_perf_table = "gold_publisher_performance_bundle"
print(f"Processing: {catalog}.{schema}.{pub_perf_table}")
drop_column_mask_if_exists(schema, pub_perf_table, "total_global_sales")
drop_column_mask_if_exists(schema, pub_perf_table, "avg_sales_per_game")

pub_revenue_mask = f"{catalog}.{schema}.mask_pub_revenue"
create_revenue_mask_function(pub_revenue_mask)
spark.sql(f"ALTER TABLE {catalog}.{schema}.{pub_perf_table} ALTER COLUMN total_global_sales SET MASK {pub_revenue_mask};")
spark.sql(f"ALTER TABLE {catalog}.{schema}.{pub_perf_table} ALTER COLUMN avg_sales_per_game SET MASK {pub_revenue_mask};")
print("  ✓ Applied masks to Publisher aggregations\n")

genre_trends_table = "gold_genre_trends_bundle"
print(f"Processing: {catalog}.{schema}.{genre_trends_table}")
drop_column_mask_if_exists(schema, genre_trends_table, "yearly_global_sales")

genre_revenue_mask = f"{catalog}.{schema}.mask_genre_revenue"
create_revenue_mask_function(genre_revenue_mask)
spark.sql(f"ALTER TABLE {catalog}.{schema}.{genre_trends_table} ALTER COLUMN yearly_global_sales SET MASK {genre_revenue_mask};")
print("  ✓ Applied mask to Genre trends\n")

print(f"\n{'='*90}")
print("SECURITY POLICIES DEPLOYMENT COMPLETE ✓")
print(f"{'='*90}\n")