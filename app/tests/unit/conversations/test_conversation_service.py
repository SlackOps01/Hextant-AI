from app.domains.conversations.schemas import ConversationResponse
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from app.domains.conversations.service import ConversationService


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


def test_create_conversation(mock_db_session, mocker: MockerFixture):
    def fake_db_refresh(instance):
        instance.id = "conv123"
        instance.pinned = False
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db_session.refresh.side_effect = fake_db_refresh

    result = ConversationService.create_conversation(mock_db_session, "user-123")
    assert result.id == "conv123"
    assert result.user_id == "user-123"
    assert result.title == "New Conversation"
    assert not result.pinned
    assert result.created_at is not None
    assert result.updated_at is not None


def test_list_conversations(mock_db_session, mocker: MockerFixture):
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        ConversationResponse(
            id="123",
            user_id="user-123",
            title="New chat",
            pinned=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
    response = ConversationService.list_conversations(mock_db_session, "user-123")
    assert len(response) == 1
    assert response[0].id == "123"
    assert response[0].title == "New chat"
    assert not response[0].pinned
    assert response[0].created_at is not None
    assert response[0].updated_at is not None


def test_delete_conversations(mock_db_session, mocker: MockerFixture):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        ConversationResponse(
            id="123",
            user_id="user-123",
            title="New chat",
            pinned=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    response = ConversationService.delete_conversation(
        mock_db_session, "user-123", "123"
    )
    assert response == {"status": "deleted"}
