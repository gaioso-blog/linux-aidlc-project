# REST API Gateway with Cognito Authorizer and CORS
resource "aws_api_gateway_rest_api" "this" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "Task Manager REST API — ${var.environment}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.common_tags
}

# ---- Cognito User Pool Authorizer ----
resource "aws_api_gateway_authorizer" "cognito" {
  name                   = "cognito-authorizer"
  rest_api_id            = aws_api_gateway_rest_api.this.id
  type                   = "COGNITO_USER_POOLS"
  identity_source        = "method.request.header.Authorization"
  provider_arns          = [var.cognito_user_pool_arn]
}

# ---- /v1 resource ----
resource "aws_api_gateway_resource" "v1" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "v1"
}

# ---- /v1/tasks ----
resource "aws_api_gateway_resource" "tasks" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.v1.id
  path_part   = "tasks"
}

resource "aws_api_gateway_resource" "task_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.tasks.id
  path_part   = "{task_id}"
}

# ---- /v1/users ----
resource "aws_api_gateway_resource" "users" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.v1.id
  path_part   = "users"
}

resource "aws_api_gateway_resource" "me" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.users.id
  path_part   = "me"
}

# ---- Helper: create a method + integration + CORS for a resource ----
module "tasks_any" {
  source       = "./method"
  rest_api_id  = aws_api_gateway_rest_api.this.id
  resource_id  = aws_api_gateway_resource.tasks.id
  http_method  = "ANY"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  lambda_invoke_arn = var.tasks_lambda_invoke_arn
}

module "task_id_any" {
  source       = "./method"
  rest_api_id  = aws_api_gateway_rest_api.this.id
  resource_id  = aws_api_gateway_resource.task_id.id
  http_method  = "ANY"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  lambda_invoke_arn = var.tasks_lambda_invoke_arn
}

module "users_any" {
  source       = "./method"
  rest_api_id  = aws_api_gateway_rest_api.this.id
  resource_id  = aws_api_gateway_resource.users.id
  http_method  = "ANY"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  lambda_invoke_arn = var.users_lambda_invoke_arn
}

module "me_any" {
  source       = "./method"
  rest_api_id  = aws_api_gateway_rest_api.this.id
  resource_id  = aws_api_gateway_resource.me.id
  http_method  = "ANY"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  lambda_invoke_arn = var.users_lambda_invoke_arn
}

# ---- Deployment ----
resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.tasks.id,
      aws_api_gateway_resource.task_id.id,
      aws_api_gateway_resource.users.id,
      aws_api_gateway_resource.me.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    module.tasks_any,
    module.task_id_any,
    module.users_any,
    module.me_any,
    aws_api_gateway_gateway_response.unauthorized,
    aws_api_gateway_gateway_response.access_denied,
    aws_api_gateway_gateway_response.default_4xx,
    aws_api_gateway_gateway_response.default_5xx,
  ]
}

resource "aws_api_gateway_stage" "this" {
  deployment_id = aws_api_gateway_deployment.this.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
  stage_name    = var.environment

  tags = local.common_tags
}

# ---- Lambda permissions (allow API Gateway to invoke Lambdas) ----
resource "aws_lambda_permission" "tasks_apigw" {
  statement_id  = "AllowAPIGatewayInvokeTasks"
  action        = "lambda:InvokeFunction"
  function_name = var.tasks_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}

resource "aws_lambda_permission" "users_apigw" {
  statement_id  = "AllowAPIGatewayInvokeUsers"
  action        = "lambda:InvokeFunction"
  function_name = var.users_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ---- Gateway Responses — add CORS headers to 4xx/5xx from API GW itself ----
# These fire when the Cognito authorizer rejects (401/403) before Lambda runs.
resource "aws_api_gateway_gateway_response" "unauthorized" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  response_type = "UNAUTHORIZED"
  status_code   = "401"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }

  response_templates = {
    "application/json" = "{\"error\": \"Unauthorized\", \"code\": \"UNAUTHORIZED\"}"
  }
}

resource "aws_api_gateway_gateway_response" "access_denied" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  response_type = "ACCESS_DENIED"
  status_code   = "403"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }

  response_templates = {
    "application/json" = "{\"error\": \"Forbidden\", \"code\": \"FORBIDDEN\"}"
  }
}

resource "aws_api_gateway_gateway_response" "default_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  response_type = "DEFAULT_4XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}

resource "aws_api_gateway_gateway_response" "default_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  response_type = "DEFAULT_5XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}
