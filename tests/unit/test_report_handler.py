"""Unit tests for report_handler Lambda."""
from unittest.mock import MagicMock, patch

import pytest

# Eager import so patch.object() can locate module-level names
import src.handlers.report_handler as report_handler_module


def _make_eventbridge_event() -> dict:
    """Minimal EventBridge scheduled event dict."""
    return {
        "version": "0",
        "id": "some-event-id",
        "source": "aws.scheduler",
        "detail-type": "Scheduled Event",
        "detail": {},
    }


def test_handler_generates_and_sends_report():
    """handler() calls ReportService.generate and NotificationService.send."""
    with (
        patch.object(report_handler_module, "ReportService") as MockReport,
        patch.object(report_handler_module, "NotificationService") as MockNotifier,
        patch.object(report_handler_module, "_list_user_emails") as mock_emails,
    ):
        mock_report_svc = MagicMock()
        mock_report_svc.generate_weekly_report.return_value = "<html>Report</html>"
        MockReport.return_value = mock_report_svc

        mock_notifier_svc = MagicMock()
        MockNotifier.return_value = mock_notifier_svc

        mock_emails.return_value = ["a@ex.com", "b@ex.com"]

        response = report_handler_module.handler(_make_eventbridge_event(), MagicMock())

    assert response["statusCode"] == 200
    mock_report_svc.generate_weekly_report.assert_called_once()
    mock_notifier_svc.send_report_email.assert_called_once_with(
        ["a@ex.com", "b@ex.com"], "<html>Report</html>"
    )


def test_handler_skips_sending_when_no_recipients():
    """handler() does not call send_report_email when no emails are found."""
    with (
        patch.object(report_handler_module, "ReportService") as MockReport,
        patch.object(report_handler_module, "NotificationService") as MockNotifier,
        patch.object(report_handler_module, "_list_user_emails") as mock_emails,
    ):
        mock_report_svc = MagicMock()
        mock_report_svc.generate_weekly_report.return_value = "<html>Report</html>"
        MockReport.return_value = mock_report_svc

        mock_notifier_svc = MagicMock()
        MockNotifier.return_value = mock_notifier_svc

        mock_emails.return_value = []

        response = report_handler_module.handler(_make_eventbridge_event(), MagicMock())

    assert response["statusCode"] == 200
    mock_notifier_svc.send_report_email.assert_not_called()


def test_handler_returns_recipient_count_in_body():
    """handler() body includes the number of recipients."""
    with (
        patch.object(report_handler_module, "ReportService") as MockReport,
        patch.object(report_handler_module, "NotificationService") as MockNotifier,
        patch.object(report_handler_module, "_list_user_emails") as mock_emails,
    ):
        MockReport.return_value.generate_weekly_report.return_value = "<html></html>"
        MockNotifier.return_value = MagicMock()
        mock_emails.return_value = ["x@ex.com", "y@ex.com", "z@ex.com"]

        response = report_handler_module.handler(_make_eventbridge_event(), MagicMock())

    assert "3" in response["body"]
