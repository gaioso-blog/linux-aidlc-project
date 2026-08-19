output "email_identity_arn" {
  description = "ARN da identidade SES"
  value       = aws_ses_email_identity.sender.arn
}

output "from_email" {
  description = "Endereço de email de envio"
  value       = aws_ses_email_identity.sender.email
}
