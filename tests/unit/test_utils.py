"""Unit tests for utility modules (config, auth)."""

import pytest

from src.utils.auth import AuthError, extract_token_from_header
from src.utils.config import get_config


class TestConfig:
    """Tests for the Config dataclass."""

    def test_config_reads_env_vars(self, monkeypatch):
        """Config correctly reads values from environment variables."""
        monkeypatch.setenv("TABLE_NAME_TASKS", "my-tasks")
        monkeypatch.setenv("TABLE_NAME_USERS", "my-users")
        monkeypatch.setenv("COGNITO_USER_POOL_ID", "us-east-1_abc")
        monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "client-xyz")
        monkeypatch.setenv("SES_FROM_EMAIL", "hi@example.com")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        config = get_config()

        assert config.table_name_tasks == "my-tasks"
        assert config.table_name_users == "my-users"
        assert config.cognito_user_pool_id == "us-east-1_abc"
        assert config.cognito_app_client_id == "client-xyz"
        assert config.ses_from_email == "hi@example.com"
        assert config.log_level == "DEBUG"

    def test_config_defaults_for_optional_vars(self, monkeypatch):
        """Config uses defaults when optional vars are missing."""
        monkeypatch.setenv("TABLE_NAME_TASKS", "t")
        monkeypatch.setenv("TABLE_NAME_USERS", "u")
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        monkeypatch.delenv("SES_FROM_EMAIL", raising=False)

        config = get_config()

        assert config.log_level == "INFO"
        assert config.ses_from_email == "noreply@example.com"

    def test_config_is_frozen(self, monkeypatch):
        """Config is immutable (frozen dataclass)."""
        monkeypatch.setenv("TABLE_NAME_TASKS", "t")
        monkeypatch.setenv("TABLE_NAME_USERS", "u")
        config = get_config()

        with pytest.raises((TypeError, AttributeError)):
            config.log_level = "DEBUG"  # type: ignore[misc]


class TestExtractTokenFromHeader:
    """Tests for the auth helper functions."""

    def test_extract_valid_bearer_token(self):
        """extract_token_from_header returns the token for a valid header."""
        token = extract_token_from_header("Bearer my-jwt-token")
        assert token == "my-jwt-token"

    def test_extract_raises_for_missing_header(self):
        """extract_token_from_header raises AuthError when header is None."""
        with pytest.raises(AuthError):
            extract_token_from_header(None)

    def test_extract_raises_for_empty_header(self):
        """extract_token_from_header raises AuthError for empty string."""
        with pytest.raises(AuthError):
            extract_token_from_header("")

    def test_extract_raises_for_non_bearer_scheme(self):
        """extract_token_from_header raises AuthError for non-Bearer scheme."""
        with pytest.raises(AuthError):
            extract_token_from_header("Basic dXNlcjpwYXNz")

    def test_extract_raises_for_malformed_header(self):
        """extract_token_from_header raises AuthError for single-word header."""
        with pytest.raises(AuthError):
            extract_token_from_header("just-a-token")
