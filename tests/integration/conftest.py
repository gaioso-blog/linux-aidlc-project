"""Shared fixtures for integration tests (moto AWS mocking)."""

import boto3
import pytest
from moto import mock_aws


@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch):
    """Inject fake AWS credentials so moto does not try real API calls."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME_TASKS", "tasks-table")
    monkeypatch.setenv("TABLE_NAME_USERS", "users-table")


@pytest.fixture
def tasks_table(aws_credentials):
    """Create a mocked DynamoDB tasks table and yield the boto3 Table resource."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="tasks-table",
            KeySchema=[{"AttributeName": "task_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "task_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield dynamodb


@pytest.fixture
def users_table(aws_credentials):
    """Create a mocked DynamoDB users table and yield the boto3 DynamoDB resource."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="users-table",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield dynamodb
