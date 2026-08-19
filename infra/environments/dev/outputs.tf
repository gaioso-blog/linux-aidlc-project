output "api_url" {
  description = "URL base da API (usar em APP_CONFIG.API_BASE_URL)"
  value       = module.api_gateway.invoke_url
}

output "frontend_url" {
  description = "URL do frontend (CloudFront)"
  value       = "https://${module.frontend.cloudfront_domain}"
}

output "frontend_bucket" {
  description = "Nome do bucket S3 do frontend"
  value       = module.frontend.bucket_name
}

output "cloudfront_distribution_id" {
  description = "ID da distribuição CloudFront (para invalidação de cache)"
  value       = module.frontend.cloudfront_distribution_id
}

output "cognito_domain" {
  description = "Domínio do Cognito Hosted UI"
  value       = module.cognito.hosted_ui_domain
}

output "cognito_client_id" {
  description = "App Client ID para o frontend"
  value       = module.cognito.app_client_id
}

output "cognito_user_pool_id" {
  description = "ID do Cognito User Pool"
  value       = module.cognito.user_pool_id
}
