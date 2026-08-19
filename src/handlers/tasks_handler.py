"""Lambda handler for task CRUD endpoints.

Routes:
    POST   /v1/tasks             — create a task
    GET    /v1/tasks             — list tasks (with optional filters)
    GET    /v1/tasks/{task_id}   — get a single task
    PUT    /v1/tasks/{task_id}   — update a task
    DELETE /v1/tasks/{task_id}   — delete a task
"""

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from src.models.task import TaskCreateRequest, TaskUpdateRequest
from src.services.task_service import TaskNotFoundError, TaskService

logger = Logger()
tracer = Tracer()
cors_config = CORSConfig(allow_origin="*", allow_headers=["Authorization", "Content-Type"])
app = APIGatewayRestResolver(cors=cors_config)

# Lazily initialised service (one instance per warm container)
_task_service: TaskService | None = None


def _get_service() -> TaskService:
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service


def _require_auth() -> dict:
    """Extract claims already validated by API Gateway Cognito authorizer."""
    try:
        # API Gateway Cognito authorizer injects claims into requestContext
        claims = app.current_event.request_context.authorizer.claims
        if not claims:
            raise UnauthorizedError("Missing auth claims")
        return claims
    except Exception as exc:
        raise UnauthorizedError("Unauthorized") from exc


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/v1/tasks")
@tracer.capture_method
def create_task():
    _require_auth()
    try:
        request = TaskCreateRequest(**app.current_event.json_body)
    except (ValidationError, TypeError) as exc:
        raise BadRequestError(f"Invalid request body: {exc}") from exc

    task = _get_service().create_task(request)
    logger.info("POST /v1/tasks", task_id=task.task_id)
    return task.model_dump(), 201


@app.get("/v1/tasks")
@tracer.capture_method
def list_tasks():
    _require_auth()
    params = app.current_event.query_string_parameters or {}
    status_filter = params.get("status")
    assignee_filter = params.get("assignee_id")

    tasks = _get_service().list_tasks(
        status_filter=status_filter,
        assignee_filter=assignee_filter,
    )
    logger.info("GET /v1/tasks", count=len(tasks))
    return {"tasks": [t.model_dump() for t in tasks], "count": len(tasks)}, 200


@app.get("/v1/tasks/<task_id>")
@tracer.capture_method
def get_task(task_id: str):
    _require_auth()
    try:
        task = _get_service().get_task(task_id)
    except TaskNotFoundError as exc:
        raise NotFoundError(str(exc)) from exc

    logger.info("GET /v1/tasks/<task_id>", task_id=task_id)
    return task.model_dump(), 200


@app.put("/v1/tasks/<task_id>")
@tracer.capture_method
def update_task(task_id: str):
    _require_auth()
    try:
        request = TaskUpdateRequest(**app.current_event.json_body)
    except (ValidationError, TypeError) as exc:
        raise BadRequestError(f"Invalid request body: {exc}") from exc

    try:
        task = _get_service().update_task(task_id, request)
    except TaskNotFoundError as exc:
        raise NotFoundError(str(exc)) from exc

    logger.info("PUT /v1/tasks/<task_id>", task_id=task_id)
    return task.model_dump(), 200


@app.delete("/v1/tasks/<task_id>")
@tracer.capture_method
def delete_task(task_id: str):
    _require_auth()
    try:
        _get_service().delete_task(task_id)
    except TaskNotFoundError as exc:
        raise NotFoundError(str(exc)) from exc

    logger.info("DELETE /v1/tasks/<task_id>", task_id=task_id)
    return {"message": "Task deleted successfully"}, 200


# ---------------------------------------------------------------------------
# Lambda entrypoint
# ---------------------------------------------------------------------------


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
