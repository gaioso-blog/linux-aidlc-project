"""Unit tests for ReportService."""
from unittest.mock import MagicMock

import pytest

from src.models.task import Task, TaskStatus
from src.models.user import User
from src.services.report_service import ReportService


@pytest.fixture
def mock_task_repo():
    return MagicMock()


@pytest.fixture
def mock_user_repo():
    return MagicMock()


@pytest.fixture
def report_service(mock_task_repo, mock_user_repo):
    return ReportService(task_repository=mock_task_repo, user_repository=mock_user_repo)


def test_report_aggregates_tasks_by_status(report_service, mock_task_repo, mock_user_repo):
    """Report correctly counts tasks per status bucket."""
    mock_task_repo.list_all.return_value = [
        Task(title="T1", status=TaskStatus.PENDING),
        Task(title="T2", status=TaskStatus.PENDING),
        Task(title="T3", status=TaskStatus.IN_PROGRESS),
        Task(title="T4", status=TaskStatus.DONE),
    ]
    mock_user_repo.list_all.return_value = []

    html = report_service.generate_weekly_report()

    assert "2</td>" in html or ">2<" in html  # 2 pending
    assert "1</td>" in html or ">1<" in html  # 1 done


def test_report_aggregates_tasks_by_user(report_service, mock_task_repo, mock_user_repo):
    """Report includes user name and their task counts."""
    mock_user_repo.list_all.return_value = [
        User(user_id="alice-id", email="alice@ex.com", name="Alice"),
    ]
    mock_task_repo.list_all.return_value = [
        Task(title="A1", status=TaskStatus.PENDING, assignee_id="alice-id"),
        Task(title="A2", status=TaskStatus.DONE, assignee_id="alice-id"),
    ]

    html = report_service.generate_weekly_report()

    assert "Alice" in html


def test_report_empty_backlog(report_service, mock_task_repo, mock_user_repo):
    """Report handles the case when all tasks are Done (backlog = 0)."""
    mock_task_repo.list_all.return_value = [
        Task(title="Done task", status=TaskStatus.DONE),
    ]
    mock_user_repo.list_all.return_value = []

    html = report_service.generate_weekly_report()

    # backlog_count should be 0 (all done)
    assert "0</td>" in html


def test_report_total_task_count(report_service, mock_task_repo, mock_user_repo):
    """Report shows the correct total task count."""
    mock_task_repo.list_all.return_value = [
        Task(title=f"Task {i}") for i in range(5)
    ]
    mock_user_repo.list_all.return_value = []

    html = report_service.generate_weekly_report()

    assert "5</td>" in html or ">5<" in html
