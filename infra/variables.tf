variable "project_name" {
  type        = string
  description = "Nome do projeto (usado como prefixo nos recursos)"
}

variable "environment" {
  type        = string
  description = "Ambiente de deploy (dev, staging, prod)"
  default     = "dev"
}

variable "region" {
  type        = string
  description = "Região AWS para deploy"
  default     = "us-east-1"
}

variable "ses_email" {
  type        = string
  description = "Endereço de email verificado no SES para envio de notificações"
}

variable "cognito_domain_prefix" {
  type        = string
  description = "Prefixo único do domínio do Cognito Hosted UI (ex: task-manager-dev)"
  default     = ""
}

variable "lambda_memory_size" {
  type        = number
  description = "Memória alocada para cada Lambda em MB"
  default     = 256
}

variable "lambda_timeout" {
  type        = number
  description = "Timeout das Lambdas em segundos"
  default     = 30
}
