# Cognito User Pool
resource "aws_cognito_user_pool" "this" {
  name = "${var.project_name}-users-${var.environment}"

  # Users sign in with email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = false
    temporary_password_validity_days = 7
  }

  # Standard attributes
  schema {
    name                     = "email"
    attribute_data_type      = "String"
    required                 = true
    mutable                  = true
    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  schema {
    name                     = "name"
    attribute_data_type      = "String"
    required                 = false
    mutable                  = true
    string_attribute_constraints {
      min_length = 1
      max_length = 100
    }
  }

  # Admin creates users manually (no self sign-up for internal tool)
  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  tags = local.common_tags
}

# App Client (SPA — public client, no secret)
resource "aws_cognito_user_pool_client" "spa" {
  name         = "${var.project_name}-spa-${var.environment}"
  user_pool_id = aws_cognito_user_pool.this.id

  # Public client — no secret
  generate_secret = false

  # OAuth2 flows
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  supported_identity_providers = ["COGNITO"]

  # Tokens validity
  access_token_validity  = 1   # hours
  id_token_validity      = 1   # hours
  refresh_token_validity = 30  # days

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  # Prevent user existence errors from leaking
  prevent_user_existence_errors = "ENABLED"
}

# Cognito Domain (Hosted UI)
resource "aws_cognito_user_pool_domain" "this" {
  domain       = var.cognito_domain_prefix != "" ? var.cognito_domain_prefix : "${var.project_name}-${var.environment}"
  user_pool_id = aws_cognito_user_pool.this.id
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
