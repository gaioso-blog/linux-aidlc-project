"""Lambda handler for the weekly report EventBridge trigger.

Triggered by: EventBridge Scheduler — every Friday at 09:00 (America/Sao_Paulo)

Flow:
    1. Generate HTML report via ReportService
    2. List all users from Cognito to get email addresses
    3. Send report email to all users via NotificationService
"""

import os

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.services.notification_service import NotificationService
from src.services.report_service import ReportService

logger = Logger()
tracer = Tracer()


def _list_user_emails() -> list[str]:
    """Retrieve all user email addresses from the Cognito User Pool."""
    user_pool_id = os.environ.get("COGNITO_USER_POOL_ID", "")
    if not user_pool_id:
        logger.warning("COGNITO_USER_POOL_ID not set, cannot list users for report")
        return []

    cognito = boto3.client(
        "cognito-idp",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    )
    emails: list[str] = []
    paginator = cognito.get_paginator("list_users")
    for page in paginator.paginate(UserPoolId=user_pool_id):
        for user in page["Users"]:
            email_attr = next(
                (a["Value"] for a in user["Attributes"] if a["Name"] == "email"),
                None,
            )
            if email_attr:
                emails.append(email_attr)

    return emails


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """EventBridge handler: generate and send the weekly report."""
    logger.info("Weekly report Lambda triggered", event=event)

    report_service = ReportService()
    notification_service = NotificationService()

    html_report = report_service.generate_weekly_report()
    recipients = _list_user_emails()

    if recipients:
        notification_service.send_report_email(recipients, html_report)
        logger.info("Weekly report dispatched", recipients_count=len(recipients))
    else:
        logger.warning("No recipients found — weekly report not sent")

    return {
        "statusCode": 200,
        "body": f"Weekly report sent to {len(recipients)} recipients.",
    }
