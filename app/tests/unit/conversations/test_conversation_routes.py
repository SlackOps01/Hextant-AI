from datetime import datetime, timezone
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.domains.conversations.routes import router
from app.core.deps import get_db, get_current_user
from app.core.oauth2 import TokenData

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def override_get_db():
    yield MagicMock(spec=Session)


def override_get_current_user():
    return TokenData(id="user-123", role="user", jti="jti-123", exp=9999999999)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_create_conversation_route(mocker: MockerFixture):
    mock_create = mocker.patch(
        "app.domains.conversations.routes.ConversationService.create_conversation"
    )

    mock_create.return_value = {
        "id": "conv-123",
        "user_id": "user-123",
        "title": "New Conversation",
        "pinned": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    response = client.post("/conversations/")

    assert response.status_code == 201
    assert response.json()["user_id"] == "user-123"
    mock_create.assert_called_once()


def test_list_conversations_route(mocker: MockerFixture):
    mock_list = mocker.patch(
        "app.domains.conversations.routes.ConversationService.list_conversations"
    )

    mock_list.return_value = [
        {
            "id": "conv-123",
            "user_id": "user-123",
            "title": "New Conversation",
            "pinned": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    ]

    response = client.get("/conversations/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_list.assert_called_once()


def test_delete_conversation_route(mocker: MockerFixture):
    mock_delete = mocker.patch(
        "app.domains.conversations.routes.ConversationService.delete_conversation"
    )

    response = client.delete("/conversations/conv-123")

    assert response.status_code == 204
    mock_delete.assert_called_once()
