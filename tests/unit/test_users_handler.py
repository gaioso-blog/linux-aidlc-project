"""Unit tests for users_handler Lambda."""

import json
from unittest.mock import MagicMock, patch

import pytest

# Eager import so patch.object() can locate the module attributes
import src.handlers.users_handler as users_handler_module


def _make_apigw_event(
    method: str,
    path: str,
    path_params: dict | None = None,
    auth_header: str = "Bearer valid-token",
) -> dict:
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": {},
        "headers": {"Authorization": auth_header},
        "body": None,
        "requestContext": {"resourcePath": path, "httpMethod": method},
    }


@pytest.fixture(autouse=True)
def mock_auth():
    with patch.object(users_handler_module, "_require_auth") as mock_validate:
        mock_validate.return_value = {
            "sub": "user-sub-001",
            "email": "dev@example.com",
            "name": "Dev User",
        }
        yield mock_validate


def test_get_current_user_returns_200():
    """GET /v1/users/me returns 200 with the user derived from JWT claims."""
    event = _make_apigw_event("GET", "/v1/users/me")
    response = users_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["user_id"] == "user-sub-001"
    assert body["email"] == "dev@example.com"


def test_list_users_returns_200():
    """GET /v1/users returns 200 with users fetched from Cognito."""
    cognito_response = {
        "Users": [
            {
                "Username": "alice",
                "Attributes": [
                    {"Name": "sub", "Value": "sub-001"},
                    {"Name": "email", "Value": "alice@ex.com"},
                    {"Name": "name", "Value": "Alice"},
                ],
            }
        ]
    }

    with patch.object(users_handler_module, "_cognito_client") as mock_cognito_factory:
        mock_cognito = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [cognito_response]
        mock_cognito.get_paginator.return_value = mock_paginator
        mock_cognito_factory.return_value = mock_cognito

        event = _make_apigw_event("GET", "/v1/users")
        response = users_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 1
    assert body["users"][0]["email"] == "alice@ex.com"


def test_list_users_unauthorized_returns_401():
    """GET /v1/users with invalid token returns 401."""
    from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

    with patch(
        "src.handlers.users_handler._require_auth", side_effect=UnauthorizedError("Unauthorized")
    ):
        event = _make_apigw_event("GET", "/v1/users", auth_header="Bearer bad-token")
        response = users_handler_module.handler(event, MagicMock())
    assert response["statusCode"] == 401
