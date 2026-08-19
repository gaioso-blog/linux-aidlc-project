"""Unit tests for TaskService."""

from unittest.mock import MagicMock

import pytest

from src.models.task import Task, TaskCreateRequest, TaskPriority, TaskStatus, TaskUpdateRequest
from src.services.task_service import TaskNotFoundError, TaskService


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_notifier():
    return MagicMock()


@pytest.fixture
def mock_user_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo, mock_notifier, mock_user_repo):
    return TaskService(
        task_repository=mock_repo,
        notification_service=mock_notifier,
        user_repository=mock_user_repo,
    )


def test_create_task_persists_and_returns_task(service, mock_repo):
    """create_task() calls repo.create and returns the new Task."""
    request = TaskCreateRequest(title="Write tests", priority=TaskPriority.HIGH)
    captured_task = None

    def capture_create(task: Task) -> Task:
        nonlocal captured_task
        captured_task = task
        return task

    mock_repo.create.side_effect = capture_create

    result = service.create_task(request)

    mock_repo.create.assert_called_once()
    assert result.title == "Write tests"
    assert result.priority == "high"
    assert captured_task is not None


def test_get_task_returns_task_when_found(service, mock_repo):
    """get_task() returns the Task when repo finds it."""
    task = Task(title="Existing task")
    mock_repo.get_by_id.return_value = task

    result = service.get_task(task.task_id)

    assert result.task_id == task.task_id
    mock_repo.get_by_id.assert_called_once_with(task.task_id)


def test_get_task_raises_not_found_when_absent(service, mock_repo):
    """get_task() raises TaskNotFoundError when repo returns None."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        service.get_task("ghost-id")


def test_assign_task_sends_notification(service, mock_repo, mock_notifier):
    """assign_task() updates the task and calls send_assignment_email."""
    task = Task(title="Assign me")
    mock_repo.get_by_id.return_value = task
    mock_repo.update.return_value = task

    service.assign_task(task.task_id, "user-42", "user42@example.com")

    mock_notifier.send_assignment_email.assert_called_once()
    call_kwargs = mock_notifier.send_assignment_email.call_args
    assert call_kwargs[1].get("assignee_email") == "user42@example.com"


def test_delete_task_removes_from_repo(service, mock_repo):
    """delete_task() verifies existence then calls repo.delete."""
    task = Task(title="Delete me")
    mock_repo.get_by_id.return_value = task

    service.delete_task(task.task_id)

    mock_repo.delete.assert_called_once_with(task.task_id)


def test_list_tasks_with_no_filters_returns_all(service, mock_repo):
    """list_tasks() with no filters calls repo.list_all."""
    mock_repo.list_all.return_value = [Task(title="A"), Task(title="B")]

    results = service.list_tasks()

    assert len(results) == 2
    mock_repo.list_all.assert_called_once()


def test_list_tasks_with_assignee_filter(service, mock_repo):
    """list_tasks(assignee_filter=...) delegates to repo.list_by_assignee."""
    mock_repo.list_by_assignee.return_value = [Task(title="Alice's task", assignee_id="alice")]

    results = service.list_tasks(assignee_filter="alice")

    assert len(results) == 1
    mock_repo.list_by_assignee.assert_called_once_with("alice")


def test_assign_task_not_found_raises(service, mock_repo):
    """assign_task() raises TaskNotFoundError when task does not exist."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        service.assign_task("ghost-id", "user-x", "x@ex.com")


def test_update_task_applies_partial_fields(service, mock_repo):
    """update_task() only updates fields present in the request."""
    original = Task(title="Original", status="pending")
    mock_repo.get_by_id.return_value = original
    mock_repo.update.return_value = original

    request = TaskUpdateRequest(title="Changed title")
    result = service.update_task(original.task_id, request)

    assert result.title == "Changed title"
    mock_repo.update.assert_called_once()


def test_update_task_all_fields(service, mock_repo, mock_notifier, mock_user_repo):
    """update_task() applies all fields including triggering notification on assignee change."""
    from src.models.user import User

    original = Task(title="Task", assignee_id="user-old")
    mock_repo.get_by_id.return_value = original
    mock_repo.update.return_value = original
    mock_user_repo.get_by_id.return_value = User(
        user_id="user-new", email="new@example.com", name="New User"
    )

    request = TaskUpdateRequest(
        title="New title",
        description="New desc",
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        assignee_id="user-new",
        due_date="2025-12-31",
        effort_estimate=5.0,
    )
    service.update_task(original.task_id, request)

    assert original.title == "New title"
    assert original.description == "New desc"
    assert original.status == "done"
    assert original.priority == "low"
    assert original.due_date == "2025-12-31"
    assert original.effort_estimate == 5.0
    mock_notifier.send_assignment_email.assert_called_once()


def test_list_tasks_with_status_filter(service, mock_repo):
    """list_tasks(status_filter=...) delegates to repo.list_by_status."""
    mock_repo.list_by_status.return_value = [Task(title="Done task", status="done")]

    results = service.list_tasks(status_filter="done")

    assert len(results) == 1
    mock_repo.list_by_status.assert_called_once_with("done")
