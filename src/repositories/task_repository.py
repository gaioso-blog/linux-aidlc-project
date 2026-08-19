"""DynamoDB repository for Task entities."""
import os
from decimal import Decimal
from typing import Any, Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key

from src.models.task import Task


def _to_dynamo(item: dict) -> dict:
    """Convert float values to Decimal for DynamoDB compatibility."""
    result = {}
    for k, v in item.items():
        if isinstance(v, float):
            result[k] = Decimal(str(v))
        elif isinstance(v, dict):
            result[k] = _to_dynamo(v)
        elif v is None:
            pass  # Skip None values — DynamoDB doesn't store nulls as attributes
        else:
            result[k] = v
    return result


def _from_dynamo(item: dict) -> dict:
    """Convert Decimal values back to float for Pydantic model compatibility."""
    result = {}
    for k, v in item.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, dict):
            result[k] = _from_dynamo(v)
        else:
            result[k] = v
    return result

class TaskRepository:
    """Handles all DynamoDB persistence for Task entities."""

    def __init__(self, table_name: str | None = None, dynamodb_resource=None) -> None:
        self._table_name = table_name or os.environ["TABLE_NAME_TASKS"]
        self._dynamodb = dynamodb_resource or boto3.resource(
            "dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        )
        self._table = self._dynamodb.Table(self._table_name)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create(self, task: Task) -> Task:
        """Persist a new task. Raises if task_id already exists."""
        self._table.put_item(
            Item=_to_dynamo(task.model_dump()),
            ConditionExpression=Attr("task_id").not_exists(),
        )
        return task

    def update(self, task: Task) -> Task:
        """Overwrite an existing task record entirely."""
        self._table.put_item(Item=_to_dynamo(task.model_dump()))
        return task

    def delete(self, task_id: str) -> None:
        """Remove a task by primary key."""
        self._table.delete_item(Key={"task_id": task_id})

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Return a single task or None if not found."""
        response = self._table.get_item(Key={"task_id": task_id})
        item = response.get("Item")
        if not item:
            return None
        return Task(**_from_dynamo(item))

    def list_all(self) -> list[Task]:
        """Return all tasks. NOTE: uses a full table scan — acceptable for ≤30 users."""
        response = self._table.scan()
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self._table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        return [Task(**_from_dynamo(item)) for item in items]

    def list_by_assignee(self, assignee_id: str) -> list[Task]:
        """Return all tasks assigned to a specific user (scan + filter)."""
        response = self._table.scan(
            FilterExpression=Attr("assignee_id").eq(assignee_id)
        )
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self._table.scan(
                FilterExpression=Attr("assignee_id").eq(assignee_id),
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
        return [Task(**_from_dynamo(item)) for item in items]

    def list_by_status(self, status: str) -> list[Task]:
        """Return all tasks with a given status (scan + filter)."""
        response = self._table.scan(
            FilterExpression=Attr("status").eq(status)
        )
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self._table.scan(
                FilterExpression=Attr("status").eq(status),
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
        return [Task(**_from_dynamo(item)) for item in items]
