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

@pytest.fixture
def mock_redis():
    from unittest.mock import AsyncMock
    mock = AsyncMock()
    mock.get.return_value = None
    return mock


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


@pytest.mark.asyncio
async def test_create_conversation(mock_db_session, mock_redis, mocker: MockerFixture):

    def fake_db_refresh(instance):
        instance.id = "conv123"
        instance.pinned = False
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db_session.refresh.side_effect = fake_db_refresh

    result = await ConversationService.create_conversation(
        mock_db_session, "user-123", mock_redis
    )

    assert result.user_id == "user-123"


@pytest.mark.asyncio
async def test_list_conversations(mock_db_session, mock_redis, fake_conversation):
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        fake_conversation
    ]

    result = await ConversationService.list_conversations(mock_db_session, "user-123", mock_redis)

    assert len(result) == 1
    mock_db_session.query.assert_called_once()


@pytest.mark.asyncio
async def test_update_conversation_success(mock_db_session, mock_redis, fake_conversation):
    update_data = ConversationUpdate(title="Updated Title")

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_conversation
    )

    result = await ConversationService.update_conversation(
        mock_db_session, update_data, "user-123", "conv-123", mock_redis
    )

    assert result.title == "Updated Title"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_conversation_not_found(mock_db_session, mock_redis):
    update_data = ConversationUpdate(title="Updated Title")

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await ConversationService.update_conversation(
            mock_db_session, update_data, "user-123", "nonexistent", mock_redis
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Conversation not found"


@pytest.mark.asyncio
async def test_delete_conversation_success(mock_db_session, mock_redis, fake_conversation):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_conversation
    )

    await ConversationService.delete_conversation(mock_db_session, "user-123", "conv-123", mock_redis)

    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_conversation_not_found(mock_db_session, mock_redis):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await ConversationService.delete_conversation(
            mock_db_session, "user-123", "nonexistent", mock_redis
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Conversation not found"
