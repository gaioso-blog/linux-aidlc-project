terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket  = "state-aidlc-terraform"
    key     = "task-manager/dev/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.region
}

# ---- DynamoDB tables ----
module "dynamodb" {
  source = "../../modules/dynamodb"

  project_name = var.project_name
  environment  = var.environment
}

# ---- Cognito User Pool ----
module "cognito" {
  source = "../../modules/cognito"

  project_name          = var.project_name
  environment           = var.environment
  cognito_domain_prefix = var.cognito_domain_prefix
  callback_urls         = ["https://${module.frontend.cloudfront_domain}/"]
  logout_urls           = ["https://${module.frontend.cloudfront_domain}/"]
}

# ---- SES identity ----
module "ses" {
  source = "../../modules/ses"

  project_name = var.project_name
  environment  = var.environment
  ses_email    = var.ses_email
}

# ---- Lambda: tasks handler ----
module "lambda_tasks" {
  source = "../../modules/lambda"

  project_name  = var.project_name
  function_name = "tasks"
  environment   = var.environment
  description   = "Task CRUD handler"
  handler       = "src.handlers.tasks_handler.handler"
  package_path  = "${path.root}/../../../dist/lambda.zip"
  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout

  environment_variables = {
    TABLE_NAME_TASKS      = module.dynamodb.tasks_table_name
    TABLE_NAME_USERS      = module.dynamodb.users_table_name
    COGNITO_USER_POOL_ID  = module.cognito.user_pool_id
    COGNITO_APP_CLIENT_ID = module.cognito.app_client_id
    SES_FROM_EMAIL        = var.ses_email
    SES_REGION            = var.region
    POWERTOOLS_SERVICE_NAME = "${var.project_name}-tasks"
    LOG_LEVEL             = "INFO"
  }

  policy_statements = {
    dynamodb = {
      effect  = "Allow"
      actions = [
        "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem",
        "dynamodb:DeleteItem", "dynamodb:Scan", "dynamodb:Query"
      ]
      resources = [
        module.dynamodb.tasks_table_arn,
        "${module.dynamodb.tasks_table_arn}/index/*",
        module.dynamodb.users_table_arn,
        "${module.dynamodb.users_table_arn}/index/*",
      ]
    }
    ses = {
      effect    = "Allow"
      actions   = ["ses:SendEmail"]
      resources = ["*"]
    }
    cognito = {
      effect    = "Allow"
      actions   = ["cognito-idp:ListUsers"]
      resources = [module.cognito.user_pool_arn]
    }
  }
}

# ---- Lambda: users handler ----
module "lambda_users" {
  source = "../../modules/lambda"

  project_name  = var.project_name
  function_name = "users"
  environment   = var.environment
  description   = "User listing handler"
  handler       = "src.handlers.users_handler.handler"
  package_path  = "${path.root}/../../../dist/lambda.zip"
  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout

  environment_variables = {
    COGNITO_USER_POOL_ID  = module.cognito.user_pool_id
    COGNITO_APP_CLIENT_ID = module.cognito.app_client_id
    POWERTOOLS_SERVICE_NAME = "${var.project_name}-users"
    LOG_LEVEL             = "INFO"
  }

  policy_statements = {
    cognito = {
      effect    = "Allow"
      actions   = ["cognito-idp:ListUsers"]
      resources = [module.cognito.user_pool_arn]
    }
  }
}

# ---- Lambda: report handler ----
module "lambda_report" {
  source = "../../modules/lambda"

  project_name  = var.project_name
  function_name = "report"
  environment   = var.environment
  description   = "Weekly report handler (EventBridge trigger)"
  handler       = "src.handlers.report_handler.handler"
  package_path  = "${path.root}/../../../dist/lambda.zip"
  memory_size   = var.lambda_memory_size
  timeout       = 120  # Reports may take longer

  environment_variables = {
    TABLE_NAME_TASKS      = module.dynamodb.tasks_table_name
    TABLE_NAME_USERS      = module.dynamodb.users_table_name
    COGNITO_USER_POOL_ID  = module.cognito.user_pool_id
    SES_FROM_EMAIL        = var.ses_email
    SES_REGION            = var.region
    POWERTOOLS_SERVICE_NAME = "${var.project_name}-report"
    LOG_LEVEL             = "INFO"
  }

  policy_statements = {
    dynamodb = {
      effect  = "Allow"
      actions = ["dynamodb:Scan", "dynamodb:Query"]
      resources = [
        module.dynamodb.tasks_table_arn,
        module.dynamodb.users_table_arn,
      ]
    }
    ses = {
      effect    = "Allow"
      actions   = ["ses:SendEmail"]
      resources = ["*"]
    }
    cognito = {
      effect    = "Allow"
      actions   = ["cognito-idp:ListUsers"]
      resources = [module.cognito.user_pool_arn]
    }
  }
}

# ---- API Gateway ----
module "api_gateway" {
  source = "../../modules/api_gateway"

  project_name               = var.project_name
  environment                = var.environment
  cognito_user_pool_arn      = module.cognito.user_pool_arn
  tasks_lambda_invoke_arn    = module.lambda_tasks.invoke_arn
  tasks_lambda_function_name = module.lambda_tasks.function_name
  users_lambda_invoke_arn    = module.lambda_users.invoke_arn
  users_lambda_function_name = module.lambda_users.function_name
}

# ---- EventBridge Scheduler ----
module "eventbridge" {
  source = "../../modules/eventbridge"

  project_name      = var.project_name
  environment       = var.environment
  report_lambda_arn = module.lambda_report.function_arn
}

# ---- Frontend (S3 + CloudFront) ----
module "frontend" {
  source = "../../modules/frontend"

  project_name = var.project_name
  environment  = var.environment
}
