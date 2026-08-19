variable "project_name" {
  type = string
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "ses_email" {
  type = string
}

variable "cognito_domain_prefix" {
  type    = string
  default = ""
}

variable "lambda_memory_size" {
  type    = number
  default = 256
}

variable "lambda_timeout" {
  type    = number
  default = 30
}
