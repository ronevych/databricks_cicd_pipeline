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