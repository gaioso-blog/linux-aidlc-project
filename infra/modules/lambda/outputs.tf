output "function_arn" {
  description = "ARN da função Lambda"
  value       = module.lambda_function.lambda_function_arn
}

output "function_name" {
  description = "Nome da função Lambda"
  value       = module.lambda_function.lambda_function_name
}

output "invoke_arn" {
  description = "ARN de invocação (para uso no API Gateway)"
  value       = module.lambda_function.lambda_function_invoke_arn
}

output "role_arn" {
  description = "ARN do execution role da Lambda"
  value       = module.lambda_function.lambda_role_arn
}
