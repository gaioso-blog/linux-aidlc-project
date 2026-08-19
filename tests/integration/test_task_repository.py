"""Integration tests for TaskRepository against a mocked DynamoDB (moto)."""
import pytest
from moto import mock_aws

from src.models.task import Task, TaskStatus
from src.repositories.task_repository import TaskRepository


@mock_aws
def test_create_and_get_task(tasks_table):
    """create() persists a task that get_by_id() can retrieve."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)
    task = Task(title="Build API", assignee_id="user-1", priority="high")

    created = repo.create(task)
    fetched = repo.get_by_id(created.task_id)

    assert fetched is not None
    assert fetched.task_id == created.task_id
    assert fetched.title == "Build API"
    assert fetched.assignee_id == "user-1"


@mock_aws
def test_get_by_id_returns_none_when_not_found(tasks_table):
    """get_by_id() returns None for a non-existent task_id."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)

    result = repo.get_by_id("does-not-exist")

    assert result is None


@mock_aws
def test_update_task(tasks_table):
    """update() overwrites the stored task with new field values."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)
    task = Task(title="Original title")
    repo.create(task)

    task.title = "Updated title"
    task.status = TaskStatus.IN_PROGRESS.value
    repo.update(task)

    fetched = repo.get_by_id(task.task_id)
    assert fetched is not None
    assert fetched.title == "Updated title"
    assert fetched.status == "in_progress"


@mock_aws
def test_delete_task(tasks_table):
    """delete() removes the task so get_by_id() returns None afterwards."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)
    task = Task(title="Task to delete")
    repo.create(task)

    repo.delete(task.task_id)
    result = repo.get_by_id(task.task_id)

    assert result is None


@mock_aws
def test_list_all_returns_all_tasks(tasks_table):
    """list_all() returns every task that was created."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)
    for i in range(3):
        repo.create(Task(title=f"Task {i}"))

    tasks = repo.list_all()

    assert len(tasks) == 3


@mock_aws
def test_list_by_assignee_filters_correctly(tasks_table):
    """list_by_assignee() returns only tasks assigned to the given user."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)
    repo.create(Task(title="Alice's task", assignee_id="alice"))
    repo.create(Task(title="Bob's task", assignee_id="bob"))
    repo.create(Task(title="Alice's second task", assignee_id="alice"))

    alice_tasks = repo.list_by_assignee("alice")
    bob_tasks = repo.list_by_assignee("bob")

    assert len(alice_tasks) == 2
    assert all(t.assignee_id == "alice" for t in alice_tasks)
    assert len(bob_tasks) == 1


@mock_aws
def test_list_by_status_filters_correctly(tasks_table):
    """list_by_status() returns only tasks with the given status."""
    repo = TaskRepository(table_name="tasks-table", dynamodb_resource=tasks_table)
    repo.create(Task(title="Pending task", status=TaskStatus.PENDING))
    repo.create(Task(title="Done task", status=TaskStatus.DONE))

    pending = repo.list_by_status("pending")
    done = repo.list_by_status("done")

    assert len(pending) == 1
    assert len(done) == 1
    assert pending[0].title == "Pending task"
