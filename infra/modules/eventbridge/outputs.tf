output "schedule_arn" {
  description = "ARN do EventBridge Scheduler"
  value       = aws_scheduler_schedule.weekly_report.arn
}
