variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "ses_email" {
  type        = string
  description = "Endereço de email para verificar no SES (from address)"
}
