variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "report_lambda_arn" {
  type        = string
  description = "ARN da Lambda de relatório semanal"
}
