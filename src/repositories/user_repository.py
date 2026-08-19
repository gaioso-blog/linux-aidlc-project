"""DynamoDB repository for User entities (cache/profile store)."""

import os

import boto3

from src.models.user import User


class UserRepository:
    """Handles DynamoDB persistence for User profile cache."""

    def __init__(self, table_name: str | None = None, dynamodb_resource=None) -> None:
        self._table_name = table_name or os.environ["TABLE_NAME_USERS"]
        self._dynamodb = dynamodb_resource or boto3.resource(
            "dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        )
        self._table = self._dynamodb.Table(self._table_name)

    def get_by_id(self, user_id: str) -> User | None:
        """Return a user by their Cognito sub UUID, or None."""
        response = self._table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        if not item:
            return None
        return User(**item)

    def save(self, user: User) -> User:
        """Upsert a user record."""
        self._table.put_item(Item=user.model_dump())
        return user

    def list_all(self) -> list[User]:
        """Return all cached users. Scans the full table."""
        response = self._table.scan()
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self._table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        return [User(**item) for item in items]
