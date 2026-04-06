terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

variable "databricks_host" {}
variable "databricks_token" {}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

resource "databricks_schema" "silver_test" {
  catalog_name = "dbr_dev"
  name         = "ronevych_silver_test"
  comment      = "Silver layer for TEST environment"
}

resource "databricks_schema" "gold_test" {
  catalog_name = "dbr_dev"
  name         = "ronevych_gold_test"
  comment      = "Gold layer for TEST environment"
}

resource "databricks_grant" "gold_usage" {
  schema = databricks_schema.gold_test.id
  privilege_assignments {
    principal  = "account users"
    privileges = ["USAGE", "SELECT"]
  }
}