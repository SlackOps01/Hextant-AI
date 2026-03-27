from datetime import datetime, timezone
from sqlalchemy.orm import Session
import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from app.domains.conversations.service import ConversationService
from app.domains.conversations.schemas import ConversationCreate
from app.domains.conversations.models import Conversations

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


