output "api_id" {
  description = "ID da REST API"
  value       = aws_api_gateway_rest_api.this.id
}

output "invoke_url" {
  description = "URL base para chamadas à API"
  value       = aws_api_gateway_stage.this.invoke_url
}

output "execution_arn" {
  description = "ARN de execução da API (para permissões Lambda)"
  value       = aws_api_gateway_rest_api.this.execution_arn
}
