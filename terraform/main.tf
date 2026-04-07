terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

# 1. Створюємо схеми
resource "databricks_schema" "bronze" {
  catalog_name = "ronevych_test"
  name         = "bronze"
}

resource "databricks_schema" "silver" {
  catalog_name = "ronevych_test"
  name         = "silver"
}

resource "databricks_schema" "gold" {
  catalog_name = "ronevych_test"
  name         = "gold"
}

# 2. Оновлюємо права (тепер на весь каталог)
resource "databricks_grants" "catalog_permissions" {
  catalog = "ronevych_test"

  grant {
    principal  = "lbiel@softserve.academy"
    privileges = ["ALL_PRIVILEGES"]
  }

  grant {
    principal  = "account users"
    privileges = ["USE_CATALOG", "USE_SCHEMA", "SELECT"]
  }
}