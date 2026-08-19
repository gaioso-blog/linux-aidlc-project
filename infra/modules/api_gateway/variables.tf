variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "cognito_user_pool_arn" {
  type        = string
  description = "ARN do Cognito User Pool para o authorizer"
}

variable "tasks_lambda_invoke_arn" {
  type        = string
  description = "ARN de invocação da Lambda de tasks"
}

variable "tasks_lambda_function_name" {
  type        = string
  description = "Nome da função Lambda de tasks (para permissão)"
}

variable "users_lambda_invoke_arn" {
  type        = string
  description = "ARN de invocação da Lambda de users"
}

variable "users_lambda_function_name" {
  type        = string
  description = "Nome da função Lambda de users (para permissão)"
}
