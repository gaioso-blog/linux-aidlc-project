variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "enable_pitr" {
  type        = bool
  description = "Habilitar Point-in-Time Recovery nas tabelas DynamoDB"
  default     = false
}
