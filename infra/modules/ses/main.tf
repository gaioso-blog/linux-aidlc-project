# SES Email Identity
# NOTE: After apply, the email address must be verified by clicking the link
# sent by AWS. Request production access (out of sandbox) separately via
# AWS Support before sending to non-verified recipients.
resource "aws_ses_email_identity" "sender" {
  email = var.ses_email
}

# Optional: configuration set for tracking
resource "aws_ses_configuration_set" "this" {
  name = "${var.project_name}-ses-config-${var.environment}"
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
