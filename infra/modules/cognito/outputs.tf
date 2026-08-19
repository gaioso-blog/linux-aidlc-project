output "user_pool_id" {
  description = "ID do Cognito User Pool"
  value       = aws_cognito_user_pool.this.id
}

output "user_pool_arn" {
  description = "ARN do Cognito User Pool (para API Gateway authorizer)"
  value       = aws_cognito_user_pool.this.arn
}

output "app_client_id" {
  description = "ID do App Client (SPA)"
  value       = aws_cognito_user_pool_client.spa.id
}

output "hosted_ui_domain" {
  description = "URL do Cognito Hosted UI"
  value       = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${var.environment == "prod" ? "us-east-1" : "us-east-1"}.amazoncognito.com"
}
