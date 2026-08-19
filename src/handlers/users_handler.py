"""Lambda handler for user endpoints.

Routes:
    GET /v1/users     — list all users from Cognito
    GET /v1/users/me  — return the current user's profile from JWT
"""

import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.models.user import User

logger = Logger()
tracer = Tracer()
cors_config = CORSConfig(allow_origin="*", allow_headers=["Authorization", "Content-Type"])
app = APIGatewayRestResolver(cors=cors_config)


def _require_auth() -> dict:
    """Extract claims already validated by API Gateway Cognito authorizer."""
    try:
        claims = app.current_event.request_context.authorizer.claims
        if not claims:
            raise UnauthorizedError("Missing auth claims")
        return claims
    except Exception as exc:
        raise UnauthorizedError("Unauthorized") from exc


def _cognito_client():
    return boto3.client(
        "cognito-idp",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    )


@app.get("/v1/users")
@tracer.capture_method
def list_users():
    _require_auth()
    user_pool_id = os.environ.get("COGNITO_USER_POOL_ID", "")
    if not user_pool_id:
        logger.error("COGNITO_USER_POOL_ID not configured")
        return {"error": "Server configuration error", "code": "SERVER_ERROR"}, 500

    cognito = _cognito_client()

    users: list[dict] = []
    paginator = cognito.get_paginator("list_users")
    for page in paginator.paginate(UserPoolId=user_pool_id):
        for cognito_user in page["Users"]:
            user = User.from_cognito_attributes(
                sub=next(
                    (a["Value"] for a in cognito_user["Attributes"] if a["Name"] == "sub"),
                    cognito_user["Username"],
                ),
                attributes=cognito_user["Attributes"],
            )
            users.append(user.model_dump())

    logger.info("GET /v1/users", count=len(users))
    return {"users": users, "count": len(users)}, 200


@app.get("/v1/users/me")
@tracer.capture_method
def get_current_user():
    claims = _require_auth()
    sub = claims.get("sub", "")
    email = claims.get("email", "")
    name = claims.get("name", email)

    user = User(user_id=sub, email=email, name=name)
    logger.info("GET /v1/users/me", user_id=sub)
    return user.model_dump(), 200


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
