module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  function_name = "${var.project_name}-${var.function_name}-${var.environment}"
  description   = var.description
  handler       = var.handler
  runtime       = "python3.13"
  timeout       = var.timeout
  memory_size   = var.memory_size

  # Use pre-built zip package instead of letting Terraform package the source
  # Build: cd workspace_root && pip install -r requirements.txt -t dist/package && cp -r src dist/package && cd dist/package && zip -r ../../dist/lambda.zip .
  create_package         = false
  local_existing_package = var.package_path

  environment_variables = var.environment_variables

  attach_policy_statements = length(var.policy_statements) > 0
  policy_statements        = var.policy_statements

  tags = local.common_tags
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
