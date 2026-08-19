"""Task domain model."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, Field, model_validator


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    """Represents a task in the task manager."""

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    assignee_id: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None, description="ISO 8601 date string (YYYY-MM-DD)")
    effort_estimate: Optional[float] = Field(
        default=None, ge=0, description="Effort estimate in hours"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    model_config = {"use_enum_values": True}

    @model_validator(mode="after")
    def validate_due_date_format(self) -> "Task":
        """Validate due_date is a valid date string if provided."""
        if self.due_date is not None:
            try:
                datetime.strptime(self.due_date, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(
                    f"due_date must be in YYYY-MM-DD format, got: {self.due_date}"
                ) from exc
        return self

    def mark_as_updated(self) -> None:
        """Update the updated_at timestamp to now."""
        self.updated_at = datetime.now(timezone.utc).isoformat()


class TaskCreateRequest(BaseModel):
    """Request body for creating a task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    assignee_id: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None)
    effort_estimate: Optional[float] = Field(default=None, ge=0)

    model_config = {"use_enum_values": True}


class TaskUpdateRequest(BaseModel):
    """Request body for updating a task (all fields optional)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=None)
    assignee_id: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None)
    effort_estimate: Optional[float] = Field(default=None, ge=0)

    model_config = {"use_enum_values": True}
