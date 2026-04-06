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

resource "databricks_grant" "admin_access" {
  # Вказуємо повний шлях до існуючої схеми текстом
  schema     = "dbr_dev.ronevych_test"
  principal  = "lbiel@softserve.academy" 
  privileges = ["ALL_PRIVILEGES"]
}

resource "databricks_grant" "others_browse" {
  schema     = "dbr_dev.ronevych_test"
  principal  = "account users"
  privileges = ["USAGE"] 
}