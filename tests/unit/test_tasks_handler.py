"""Unit tests for tasks_handler Lambda."""

import json
from unittest.mock import MagicMock, patch

import pytest

# Import handler module eagerly so patch() can locate the target
import src.handlers.tasks_handler as tasks_handler_module
from src.models.task import Task, TaskPriority, TaskStatus


def _make_apigw_event(
    method: str,
    path: str,
    body: dict | None = None,
    path_params: dict | None = None,
    query_params: dict | None = None,
    auth_header: str = "Bearer valid-token",
) -> dict:
    """Build a minimal API Gateway proxy event dict."""
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": query_params or {},
        "headers": {"Authorization": auth_header},
        "body": json.dumps(body) if body else None,
        "requestContext": {"resourcePath": path, "httpMethod": method},
    }


@pytest.fixture(autouse=True)
def reset_service():
    """Reset the module-level lazy service singleton between tests."""
    tasks_handler_module._task_service = None
    yield
    tasks_handler_module._task_service = None


@pytest.fixture(autouse=True)
def mock_auth():
    """Patch _require_auth to always return valid claims (API GW authorizer already validated token)."""
    with patch.object(tasks_handler_module, "_require_auth") as mock_req:
        mock_req.return_value = {"sub": "user-test-sub", "email": "test@ex.com"}
        yield mock_req


def test_create_task_happy_path():
    """POST /v1/tasks returns 201 with the new task."""
    task = Task(title="New task", priority=TaskPriority.HIGH)

    with patch.object(tasks_handler_module, "_get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.create_task.return_value = task
        mock_svc_factory.return_value = mock_svc

        event = _make_apigw_event(
            "POST", "/v1/tasks", body={"title": "New task", "priority": "high"}
        )
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["title"] == "New task"


def test_create_task_invalid_body_returns_400():
    """POST /v1/tasks with missing required field returns 400."""
    with patch.object(tasks_handler_module, "_get_service"):
        event = _make_apigw_event("POST", "/v1/tasks", body={"priority": "high"})  # missing title
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 400


def test_get_task_found_returns_200():
    """GET /v1/tasks/{task_id} returns 200 with the task."""
    task = Task(title="Existing task")

    with patch.object(tasks_handler_module, "_get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.get_task.return_value = task
        mock_svc_factory.return_value = mock_svc

        event = _make_apigw_event(
            "GET",
            f"/v1/tasks/{task.task_id}",
            path_params={"task_id": task.task_id},
        )
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["title"] == "Existing task"


def test_get_task_not_found_returns_404():
    """GET /v1/tasks/{task_id} returns 404 when task does not exist."""
    from src.services.task_service import TaskNotFoundError

    with patch.object(tasks_handler_module, "_get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.get_task.side_effect = TaskNotFoundError("not found")
        mock_svc_factory.return_value = mock_svc

        event = _make_apigw_event("GET", "/v1/tasks/ghost", path_params={"task_id": "ghost"})
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 404


def test_list_tasks_returns_200():
    """GET /v1/tasks returns 200 with a list of tasks."""
    tasks = [Task(title="T1"), Task(title="T2")]

    with patch.object(tasks_handler_module, "_get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.list_tasks.return_value = tasks
        mock_svc_factory.return_value = mock_svc

        event = _make_apigw_event("GET", "/v1/tasks")
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 2


def test_update_task_returns_200():
    """PUT /v1/tasks/{task_id} returns 200 with the updated task."""
    task = Task(title="Updated task", status=TaskStatus.IN_PROGRESS)

    with patch.object(tasks_handler_module, "_get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.update_task.return_value = task
        mock_svc_factory.return_value = mock_svc

        event = _make_apigw_event(
            "PUT",
            f"/v1/tasks/{task.task_id}",
            body={"status": "in_progress"},
            path_params={"task_id": task.task_id},
        )
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 200


def test_delete_task_returns_200():
    """DELETE /v1/tasks/{task_id} returns 200 on success."""
    task_id = "task-to-delete"

    with patch.object(tasks_handler_module, "_get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.delete_task.return_value = None
        mock_svc_factory.return_value = mock_svc

        event = _make_apigw_event(
            "DELETE", f"/v1/tasks/{task_id}", path_params={"task_id": task_id}
        )
        response = tasks_handler_module.handler(event, MagicMock())

    assert response["statusCode"] == 200


def test_missing_auth_header_returns_401():
    """GET /v1/tasks with missing auth claims returns 401."""
    from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

    with patch(
        "src.handlers.tasks_handler._require_auth", side_effect=UnauthorizedError("Unauthorized")
    ):
        event = _make_apigw_event("GET", "/v1/tasks", auth_header="")
        response = tasks_handler_module.handler(event, MagicMock())
    assert response["statusCode"] == 401
