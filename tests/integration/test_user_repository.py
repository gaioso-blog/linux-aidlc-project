"""Integration tests for UserRepository against a mocked DynamoDB (moto)."""
from moto import mock_aws

from src.models.user import User
from src.repositories.user_repository import UserRepository


@mock_aws
def test_save_and_get_user(users_table):
    """save() persists a user that get_by_id() can retrieve."""
    repo = UserRepository(table_name="users-table", dynamodb_resource=users_table)
    user = User(user_id="sub-001", email="dev@example.com", name="Dev User")

    repo.save(user)
    fetched = repo.get_by_id("sub-001")

    assert fetched is not None
    assert fetched.user_id == "sub-001"
    assert fetched.email == "dev@example.com"
    assert fetched.name == "Dev User"


@mock_aws
def test_get_by_id_returns_none_for_unknown_user(users_table):
    """get_by_id() returns None when user does not exist."""
    repo = UserRepository(table_name="users-table", dynamodb_resource=users_table)

    result = repo.get_by_id("unknown-sub")

    assert result is None


@mock_aws
def test_list_all_returns_all_users(users_table):
    """list_all() returns every saved user."""
    repo = UserRepository(table_name="users-table", dynamodb_resource=users_table)
    repo.save(User(user_id="sub-001", email="a@ex.com", name="Alice"))
    repo.save(User(user_id="sub-002", email="b@ex.com", name="Bob"))

    users = repo.list_all()

    assert len(users) == 2
    emails = {u.email for u in users}
    assert "a@ex.com" in emails
    assert "b@ex.com" in emails
