# EventBridge Scheduler — Weekly report every Friday at 09:00 (America/Sao_Paulo)
resource "aws_scheduler_schedule" "weekly_report" {
  name                         = "${var.project_name}-weekly-report-${var.environment}"
  description                  = "Dispara relatório semanal toda sexta-feira às 09:00"
  schedule_expression          = "cron(0 9 ? * FRI *)"
  schedule_expression_timezone = "America/Sao_Paulo"
  state                        = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = var.report_lambda_arn
    role_arn = aws_iam_role.scheduler.arn
  }
}

# IAM Role for EventBridge Scheduler to invoke Lambda
resource "aws_iam_role" "scheduler" {
  name = "${var.project_name}-scheduler-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "invoke_lambda" {
  name = "invoke-report-lambda"
  role = aws_iam_role.scheduler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = var.report_lambda_arn
      }
    ]
  })
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
