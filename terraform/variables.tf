variable "catalog" {
  description = "The catalog name for Databricks resources"
  type        = string
  default     = "ronevych_test"
}

variable "schema" {
  description = "The schema name for Databricks resources"
  type        = string
  default     = "gold"
}

variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "databricks_token" {
  description = "Databricks API token"
  type        = string
  sensitive   = true
}

variable "sql_warehouse_id" {
  description = "SQL Warehouse ID for dashboard"
  type        = string
  default     = "a1f04664c7fcffa4"
}
