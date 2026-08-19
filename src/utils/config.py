"""Application configuration loaded from environment variables."""
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    """Immutable configuration object built from environment variables."""

    table_name_tasks: str = field(default_factory=lambda: os.environ["TABLE_NAME_TASKS"])
    table_name_users: str = field(default_factory=lambda: os.environ["TABLE_NAME_USERS"])
    cognito_user_pool_id: str = field(
        default_factory=lambda: os.environ.get("COGNITO_USER_POOL_ID", "")
    )
    cognito_app_client_id: str = field(
        default_factory=lambda: os.environ.get("COGNITO_APP_CLIENT_ID", "")
    )
    ses_from_email: str = field(
        default_factory=lambda: os.environ.get("SES_FROM_EMAIL", "noreply@example.com")
    )
    ses_region: str = field(
        default_factory=lambda: os.environ.get("SES_REGION", "us-east-1")
    )
    aws_region: str = field(
        default_factory=lambda: os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    )
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    service_name: str = field(
        default_factory=lambda: os.environ.get("POWERTOOLS_SERVICE_NAME", "task-manager")
    )


def get_config() -> Config:
    """Return a Config instance populated from the current environment."""
    return Config()
