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

resource "databricks_schema" "test_schema" {
  catalog_name = "dbr_dev"
  name         = "ronevych_test"
  comment      = "Managed by Terraform: Isolated schema for Lab 7 testing"
}

resource "databricks_grant" "admin_access" {
  schema     = databricks_schema.test_schema.id
  principal  = "lbiel@softserve.academy" 
  privileges = ["ALL_PRIVILEGES"]
}

resource "databricks_grant" "others_browse" {
  schema     = databricks_schema.test_schema.id
  principal  = "account users"
  privileges = ["USAGE", "BROWSE"] 
}