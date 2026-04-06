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

resource "databricks_catalog" "test_catalog" {
  name    = "ronevych_test"
  comment = "Catalog for Lab 7 TEST environment"
}

resource "databricks_grant" "admin_access" {
  catalog    = databricks_catalog.test_catalog.name
  principal  = "lbiel@softserve.academy" # Перевір спелінг email!
  privileges = ["ALL_PRIVILEGES"]
}

resource "databricks_grant" "others_browse" {
  catalog    = databricks_catalog.test_catalog.name
  principal  = "account users"
  # Для каталогу використовуємо USE_CATALOG та BROWSE
  privileges = ["USE_CATALOG", "BROWSE"] 
}