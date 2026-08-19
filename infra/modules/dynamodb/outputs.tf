output "tasks_table_name" {
  description = "Nome da tabela DynamoDB de tasks"
  value       = aws_dynamodb_table.tasks.name
}

output "tasks_table_arn" {
  description = "ARN da tabela DynamoDB de tasks"
  value       = aws_dynamodb_table.tasks.arn
}

output "users_table_name" {
  description = "Nome da tabela DynamoDB de users"
  value       = aws_dynamodb_table.users.name
}

output "users_table_arn" {
  description = "ARN da tabela DynamoDB de users"
  value       = aws_dynamodb_table.users.arn
}
