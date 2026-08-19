output "bucket_name" {
  description = "Nome do S3 bucket do frontend"
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_domain" {
  description = "Domínio do CloudFront (usar como URL do frontend)"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_distribution_id" {
  description = "ID da distribuição CloudFront"
  value       = aws_cloudfront_distribution.frontend.id
}
