from datetime import datetime, timezone
from sqlalchemy.orm import Session
import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from fastapi import HTTPException
from app.domains.conversations.service import (
    ConversationService,
    ConversationNotFoundException,
)
from app.domains.conversations.schemas import ConversationCreate, ConversationUpdate
from app.domains.conversations.models import Conversations


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


<<<<<<< Updated upstream
@pytest.fixture
def fake_conversation():
    return Conversations(
        id="conv-123",
        user_id="user-123",
        title="Test Conversation",
        pinned=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


=======
>>>>>>> Stashed changes
def test_create_conversation(mock_db_session, mocker: MockerFixture):
    fake_conversation_create = ConversationCreate(title="Fake convo")

    def fake_db_refresh(instance):
        instance.id = "conv123"
        instance.pinned = False
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db_session.refresh.side_effect = fake_db_refresh

<<<<<<< Updated upstream
    result = ConversationService.create_conversation(mock_db_session, "user-123")
=======
    result = ConversationService.create_conversation(
        mock_db_session, "user-123", fake_conversation_create
    )
>>>>>>> Stashed changes

    assert result.user_id == "user-123"


<<<<<<< Updated upstream
def test_list_conversations(mock_db_session, fake_conversation):
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        fake_conversation
    ]

    result = ConversationService.list_conversations(mock_db_session, "user-123")

    assert len(result) == 1
    mock_db_session.query.assert_called_once()


def test_update_conversation_success(mock_db_session, fake_conversation):
    update_data = ConversationUpdate(title="Updated Title")

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_conversation
    )

    result = ConversationService.update_conversation(
        mock_db_session, update_data, "user-123", "conv-123"
    )

    assert result.title == "Updated Title"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_update_conversation_not_found(mock_db_session):
    update_data = ConversationUpdate(title="Updated Title")

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        ConversationService.update_conversation(
            mock_db_session, update_data, "user-123", "nonexistent"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Conversation not found"


def test_delete_conversation_success(mock_db_session, fake_conversation):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_conversation
    )

    ConversationService.delete_conversation(mock_db_session, "user-123", "conv-123")

    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_delete_conversation_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        ConversationService.delete_conversation(
            mock_db_session, "user-123", "nonexistent"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Conversation not found"
=======
def test_
>>>>>>> Stashed changes
