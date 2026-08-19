"""Unit tests for Pydantic data models."""
import pytest
from pydantic import ValidationError

from src.models.task import Task, TaskCreateRequest, TaskPriority, TaskStatus, TaskUpdateRequest
from src.models.user import User


class TestTaskModel:
    """Tests for the Task Pydantic model."""

    def test_task_creation_with_required_fields_only(self):
        """Task can be created with only the required title field."""
        task = Task(title="Review pull request")

        assert task.title == "Review pull request"
        assert task.status == TaskStatus.PENDING.value
        assert task.priority == TaskPriority.MEDIUM.value
        assert task.task_id is not None
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_requires_title(self):
        """Task raises ValidationError when title is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Task()  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "title" in field_names

    def test_task_rejects_invalid_status(self):
        """Task raises ValidationError for an unknown status value."""
        with pytest.raises(ValidationError):
            Task(title="Test", status="unknown_status")  # type: ignore[arg-type]

    def test_task_rejects_invalid_priority(self):
        """Task raises ValidationError for an unknown priority value."""
        with pytest.raises(ValidationError):
            Task(title="Test", priority="ultra")  # type: ignore[arg-type]

    def test_task_with_all_optional_fields(self):
        """Task accepts all optional fields when provided."""
        task = Task(
            title="Implement feature",
            description="Detailed description here",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            assignee_id="user-abc-123",
            due_date="2025-12-31",
            effort_estimate=8.5,
        )

        assert task.description == "Detailed description here"
        assert task.assignee_id == "user-abc-123"
        assert task.due_date == "2025-12-31"
        assert task.effort_estimate == 8.5
        assert task.status == "in_progress"
        assert task.priority == "high"

    def test_task_serialization_to_dict(self):
        """Task.model_dump() produces a plain dict with correct keys."""
        task = Task(title="Deploy service", assignee_id="user-1")
        data = task.model_dump()

        assert isinstance(data, dict)
        required_keys = {
            "task_id",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "due_date",
            "effort_estimate",
            "created_at",
            "updated_at",
        }
        assert required_keys.issubset(data.keys())
        assert data["title"] == "Deploy service"

    def test_task_rejects_invalid_due_date_format(self):
        """Task raises ValidationError when due_date is not YYYY-MM-DD."""
        with pytest.raises(ValidationError):
            Task(title="Test", due_date="31/12/2025")

    def test_task_rejects_negative_effort_estimate(self):
        """Task raises ValidationError when effort_estimate is negative."""
        with pytest.raises(ValidationError):
            Task(title="Test", effort_estimate=-1.0)

    def test_task_unique_ids_generated_by_default(self):
        """Each Task instance gets a unique task_id."""
        task_a = Task(title="Task A")
        task_b = Task(title="Task B")

        assert task_a.task_id != task_b.task_id


class TestTaskUpdateRequest:
    """Tests for the TaskUpdateRequest model."""

    def test_update_request_all_fields_optional(self):
        """TaskUpdateRequest can be instantiated with no fields."""
        req = TaskUpdateRequest()
        assert req.title is None
        assert req.status is None

    def test_update_request_accepts_valid_status(self):
        """TaskUpdateRequest accepts a valid status string."""
        req = TaskUpdateRequest(status=TaskStatus.DONE)
        assert req.status == "done"


class TestUserModel:
    """Tests for the User Pydantic model."""

    def test_user_creation_with_required_fields(self):
        """User can be created with all required fields."""
        user = User(user_id="sub-123", email="dev@example.com", name="Dev User")

        assert user.user_id == "sub-123"
        assert user.email == "dev@example.com"
        assert user.name == "Dev User"

    def test_user_from_cognito_attributes(self):
        """User.from_cognito_attributes parses Cognito attribute list correctly."""
        attributes = [
            {"Name": "email", "Value": "alice@example.com"},
            {"Name": "name", "Value": "Alice"},
        ]
        user = User.from_cognito_attributes(sub="cognito-sub-001", attributes=attributes)

        assert user.user_id == "cognito-sub-001"
        assert user.email == "alice@example.com"
        assert user.name == "Alice"
