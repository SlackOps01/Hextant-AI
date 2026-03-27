from pytest_mock import MockFixture
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.domains.users.service import UserService
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate
from fastapi import HTTPException
from datetime import datetime, timezone


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def fake_user():
    return User(
        id="123",
        email="[EMAIL_ADDRESS]",
        username="testuser",
        password="hashedpassword",
        role="user",
    )


def test_get_user_by_id(mock_db_session, fake_user):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_user
    )

    result = UserService.get_user_by_id(mock_db_session, "123")
    assert result.id == "123"


def test_get_user_by_email(mock_db_session, fake_user):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_user
    )

    result = UserService.get_user_by_email(mock_db_session, "[EMAIL_ADDRESS]")

    assert result.email == "[EMAIL_ADDRESS]"


def test_user_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        UserService.get_user_by_id(mock_db_session, "NO")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_create_user(mock_db_session, mocker: MockFixture):
    new_user = UserCreate(
        username="lanre", email="olanrewajusholarin5@gmail.com", password="lancelot"
    )

    mock_hash_password = mocker.patch("app.domains.users.service.hash_password")
    mock_hash_password.return_value = "supersecretpassword"

    def fake_db_refresh(instance):
        # We manually attach the missing fields to the object
        instance.id = "123-uuid"
        instance.role = "user"
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    # 2. Tell the mock to trigger that function whenever db.refresh is called!
    mock_db_session.refresh.side_effect = fake_db_refresh

    result = UserService.create_user(mock_db_session, new_user)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    mock_hash_password.assert_called_once_with("lancelot")

    assert result.username == "lanre"


def test_delete_user(mock_db_session, mocker: MockFixture):
    mock_db_session.query.return_value.first.return_value = fake_user

    result = UserService.delete_user(mock_db_session, "id")

    mock_db_session.delete.assert_called_once()
    assert result["status"] == "success"
