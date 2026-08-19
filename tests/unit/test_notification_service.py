"""Unit tests for NotificationService."""

from unittest.mock import MagicMock

import pytest

from src.models.task import Task, TaskPriority
from src.services.notification_service import NotificationService


@pytest.fixture
def mock_ses():
    return MagicMock()


@pytest.fixture
def notifier(mock_ses):
    service = NotificationService(ses_client=mock_ses)
    return service


def test_send_assignment_email_calls_ses(notifier, mock_ses):
    """send_assignment_email() invokes ses.send_email with correct addresses."""
    task = Task(title="Review architecture", priority=TaskPriority.HIGH)

    result = notifier.send_assignment_email(task, assignee_email="dev@example.com")

    assert result is True
    mock_ses.send_email.assert_called_once()
    call_kwargs = mock_ses.send_email.call_args[1]
    assert "dev@example.com" in call_kwargs["Destination"]["ToAddresses"]


def test_send_assignment_email_subject_contains_task_title(notifier, mock_ses):
    """The email subject must include the task title."""
    task = Task(title="Deploy to production")

    notifier.send_assignment_email(task, assignee_email="ops@example.com")

    call_kwargs = mock_ses.send_email.call_args[1]
    subject = call_kwargs["Message"]["Subject"]["Data"]
    assert "Deploy to production" in subject


def test_send_assignment_email_skips_when_no_email(notifier, mock_ses):
    """send_assignment_email() returns False and does NOT call SES when email is missing."""
    task = Task(title="Orphaned task")

    result = notifier.send_assignment_email(task, assignee_email=None)

    assert result is False
    mock_ses.send_email.assert_not_called()


def test_send_report_email_calls_ses_for_multiple_recipients(notifier, mock_ses):
    """send_report_email() calls SES once with all addresses in ToAddresses."""
    recipients = ["alice@ex.com", "bob@ex.com"]
    html_body = "<html><body>Report</body></html>"

    notifier.send_report_email(recipients, html_body)

    mock_ses.send_email.assert_called_once()
    call_kwargs = mock_ses.send_email.call_args[1]
    assert set(call_kwargs["Destination"]["ToAddresses"]) == set(recipients)


def test_send_report_email_skips_empty_recipients(notifier, mock_ses):
    """send_report_email() does not call SES when recipient list is empty."""
    notifier.send_report_email([], "<html></html>")
    mock_ses.send_email.assert_not_called()


def test_assignment_email_html_contains_task_details(notifier, mock_ses):
    """The HTML email body includes task title and priority."""
    task = Task(
        title="Critical deployment",
        priority=TaskPriority.HIGH,
        description="Deploy to prod",
        due_date="2025-12-31",
        effort_estimate=4.0,
    )

    notifier.send_assignment_email(task, assignee_email="ops@example.com")

    call_kwargs = mock_ses.send_email.call_args[1]
    html = call_kwargs["Message"]["Body"]["Html"]["Data"]
    assert "Critical deployment" in html
    assert "high" in html
    assert "2025-12-31" in html
