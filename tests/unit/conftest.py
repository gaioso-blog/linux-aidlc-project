"""Shared fixtures for unit tests."""
import os

import pytest


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    """Set required environment variables for all unit tests."""
    monkeypatch.setenv("TABLE_NAME_TASKS", "tasks-table")
    monkeypatch.setenv("TABLE_NAME_USERS", "users-table")
    monkeypatch.setenv("COGNITO_USER_POOL_ID", "us-east-1_test123")
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("SES_FROM_EMAIL", "noreply@test.com")
    monkeypatch.setenv("SES_REGION", "us-east-1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "task-manager-test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
