"""Email notification service via Amazon SES."""

import os

import boto3
from aws_lambda_powertools import Logger

from src.models.task import Task

logger = Logger(child=True)


class NotificationService:
    """Sends transactional emails via Amazon SES."""

    def __init__(self, ses_client=None) -> None:
        self._ses = ses_client or boto3.client(
            "ses", region_name=os.environ.get("SES_REGION", "us-east-1")
        )
        self._from_email = os.environ.get("SES_FROM_EMAIL", "noreply@example.com")

    def send_assignment_email(
        self, task: Task, assignee_email: str | None = None, assignee_id: str | None = None
    ) -> bool:
        """
        Send an assignment notification email.

        Returns True if the email was dispatched, False if skipped (no email address).
        """
        if not assignee_email:
            logger.warning(
                "Skipping assignment email — no email address provided",
                task_id=task.task_id,
                assignee_id=assignee_id,
            )
            return False

        subject = f"[Task Manager] Nova tarefa atribuída: {task.title}"
        html_body = self._build_assignment_email_body(task)
        text_body = (
            f"Você recebeu uma nova tarefa: {task.title}\n"
            f"Prioridade: {task.priority}\n"
            f"Status: {task.status}\n"
        )
        if task.due_date:
            text_body += f"Prazo: {task.due_date}\n"

        try:
            self._ses.send_email(
                Source=self._from_email,
                Destination={"ToAddresses": [assignee_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                    },
                },
            )
            logger.info(
                "Assignment email sent",
                to=assignee_email,
                task_id=task.task_id,
            )
            return True
        except Exception as exc:
            logger.error(
                "Failed to send assignment email",
                error=str(exc),
                task_id=task.task_id,
            )
            raise

    def _build_assignment_email_body(self, task: Task) -> str:
        """Build an HTML email body for task assignment."""
        due_row = (
            f"<tr><td><strong>Prazo:</strong></td><td>{task.due_date}</td></tr>"
            if task.due_date
            else ""
        )
        effort_row = (
            f"<tr><td><strong>Estimativa:</strong></td><td>{task.effort_estimate}h</td></tr>"
            if task.effort_estimate is not None
            else ""
        )
        description_section = (
            f"<p><strong>Descrição:</strong><br>{task.description}</p>" if task.description else ""
        )

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <h2 style="color: #2c3e50;">Nova Tarefa Atribuída</h2>
            <p>Uma nova tarefa foi atribuída a você no Task Manager:</p>
            <table style="border-collapse: collapse; width: 100%;">
                <tr><td><strong>Título:</strong></td><td>{task.title}</td></tr>
                <tr><td><strong>Prioridade:</strong></td><td>{task.priority}</td></tr>
                <tr><td><strong>Status:</strong></td><td>{task.status}</td></tr>
                {due_row}
                {effort_row}
            </table>
            {description_section}
            <hr>
            <p style="color: #7f8c8d; font-size: 12px;">Task Manager — Uso interno</p>
        </body>
        </html>
        """

    def send_report_email(self, to_addresses: list[str], html_body: str) -> None:
        """Send the weekly report email to a list of recipients."""
        if not to_addresses:
            logger.warning("No recipients for weekly report, skipping")
            return

        subject = "[Task Manager] Relatório Semanal de Progresso"

        try:
            self._ses.send_email(
                Source=self._from_email,
                Destination={"ToAddresses": to_addresses},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {
                            "Data": "Relatório semanal disponível. Veja a versão HTML.",
                            "Charset": "UTF-8",
                        },
                    },
                },
            )
            logger.info("Weekly report email sent", recipients=len(to_addresses))
        except Exception as exc:
            logger.error(
                "Failed to send weekly report email",
                error=str(exc),
                recipients_count=len(to_addresses),
            )
            raise
