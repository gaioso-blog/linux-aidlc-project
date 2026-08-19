"""Business logic for Task management."""

import os

import boto3
from aws_lambda_powertools import Logger

from src.models.task import Task, TaskCreateRequest, TaskUpdateRequest
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.services.notification_service import NotificationService

logger = Logger(child=True)


class TaskNotFoundError(Exception):
    """Raised when a task cannot be found by its ID."""


class TaskService:
    """Coordinates task CRUD and notifications."""

    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        notification_service: NotificationService | None = None,
        user_repository: UserRepository | None = None,
    ) -> None:
        self._repo = task_repository or TaskRepository()
        self._notifier = notification_service or NotificationService()
        self._user_repo = user_repository or UserRepository()

    def create_task(self, request: TaskCreateRequest) -> Task:
        """Create and persist a new task. Sends notification if assignee is set."""
        task = Task(
            title=request.title,
            description=request.description,
            priority=request.priority,
            assignee_id=request.assignee_id,
            due_date=request.due_date,
            effort_estimate=request.effort_estimate,
        )
        created = self._repo.create(task)
        logger.info("Task created", task_id=created.task_id, title=created.title)
        # Send notification if assignee was set at creation time
        if request.assignee_id:
            assignee_email = self._get_user_email(request.assignee_id)
            self._notifier.send_assignment_email(
                created, assignee_email=assignee_email, assignee_id=request.assignee_id
            )
        return created

    def get_task(self, task_id: str) -> Task:
        """Return a task by ID, raising TaskNotFoundError if absent."""
        task = self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return task

    def update_task(self, task_id: str, request: TaskUpdateRequest) -> Task:
        """Apply partial updates to an existing task."""
        task = self.get_task(task_id)

        if request.title is not None:
            task.title = request.title
        if request.description is not None:
            task.description = request.description
        if request.status is not None:
            task.status = request.status
        if request.priority is not None:
            task.priority = request.priority
        if request.assignee_id is not None:
            old_assignee = task.assignee_id
            task.assignee_id = request.assignee_id
            # Send notification when assignee changes — resolve email first
            if old_assignee != request.assignee_id:
                assignee_email = self._get_user_email(request.assignee_id)
                self._notifier.send_assignment_email(
                    task, assignee_email=assignee_email, assignee_id=request.assignee_id
                )
        if request.due_date is not None:
            task.due_date = request.due_date
        if request.effort_estimate is not None:
            task.effort_estimate = request.effort_estimate

        task.mark_as_updated()
        updated = self._repo.update(task)
        logger.info("Task updated", task_id=task_id)
        return updated

    def delete_task(self, task_id: str) -> None:
        """Delete a task. Raises TaskNotFoundError if not found."""
        self.get_task(task_id)  # Verify existence before deleting
        self._repo.delete(task_id)
        logger.info("Task deleted", task_id=task_id)

    def assign_task(self, task_id: str, assignee_id: str, assignee_email: str) -> Task:
        """Assign a task to a user and send an email notification."""
        task = self.get_task(task_id)
        task.assignee_id = assignee_id
        task.mark_as_updated()
        updated = self._repo.update(task)
        self._notifier.send_assignment_email(task, assignee_email=assignee_email)
        logger.info("Task assigned", task_id=task_id, assignee_id=assignee_id)
        return updated

    def _get_user_email(self, user_id: str) -> str | None:
        """Resolve user email: try DynamoDB cache first, then Cognito directly."""
        # Try DynamoDB cache
        user = self._user_repo.get_by_id(user_id)
        if user and user.email:
            return user.email

        # Fallback: query Cognito directly by sub
        try:
            user_pool_id = os.environ.get("COGNITO_USER_POOL_ID", "")
            if not user_pool_id:
                return None
            cognito = boto3.client(
                "cognito-idp", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            )
            resp = cognito.list_users(
                UserPoolId=user_pool_id,
                Filter=f'sub = "{user_id}"',
                Limit=1,
            )
            users = resp.get("Users", [])
            if users:
                attrs = {a["Name"]: a["Value"] for a in users[0].get("Attributes", [])}
                return attrs.get("email")
        except Exception as exc:
            logger.warning(
                "Failed to resolve user email from Cognito", user_id=user_id, error=str(exc)
            )
        return None

    def list_tasks(
        self,
        status_filter: str | None = None,
        assignee_filter: str | None = None,
    ) -> list[Task]:
        """List tasks with optional filters for status and assignee.

        When both filters are provided, list_all is used and both are applied
        in-memory to ensure correct results regardless of parameter order.
        """
        if status_filter and assignee_filter:
            # Both filters: scan all and apply both in-memory
            tasks = self._repo.list_all()
            tasks = [
                t for t in tasks if t.status == status_filter and t.assignee_id == assignee_filter
            ]
        elif assignee_filter:
            tasks = self._repo.list_by_assignee(assignee_filter)
        elif status_filter:
            tasks = self._repo.list_by_status(status_filter)
        else:
            tasks = self._repo.list_all()

        return tasks
