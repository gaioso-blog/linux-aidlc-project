variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "cognito_domain_prefix" {
  type        = string
  description = "Prefixo único do Cognito Hosted UI domain"
  default     = ""
}

variable "callback_urls" {
  type        = list(string)
  description = "URLs de callback OAuth2 permitidas (ex: CloudFront URL)"
  default     = ["http://localhost:8080/"]
}

variable "logout_urls" {
  type        = list(string)
  description = "URLs de logout OAuth2 permitidas"
  default     = ["http://localhost:8080/"]
}
