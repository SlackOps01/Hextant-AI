from datetime import datetime, timezone
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.domains.tiers.routes import router
from app.core.deps import get_db
from app.domains.users.security import require_admin

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def override_get_db():
    yield MagicMock(spec=Session)


def override_require_admin():
    return {"id": "admin-123", "role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_admin] = override_require_admin


def test_create_tier_route(mocker: MockerFixture):
    mock_create = mocker.patch("app.domains.tiers.routes.TierService.create_tier")

    mock_create.return_value = {
        "id": "tier-123",
        "name": "Pro",
        "price": 2000,
        "message_limit": 1000,
        "image_limit": 100,
        "research_limit": 50,
        "document_limit": 100,
        "model_access": ["gpt-4", "claude-3"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    payload = {
        "name": "Pro",
        "price": 2000,
        "message_limit": 1000,
        "image_limit": 100,
        "research_limit": 50,
        "document_limit": 100,
        "model_access": ["gpt-4", "claude-3"],
        "is_active": True,
    }

    response = client.post("/tiers/", json=payload)

    assert response.status_code == 201
    assert response.json()["name"] == "Pro"
    mock_create.assert_called_once()


def test_list_tiers_route(mocker: MockerFixture):
    mock_list = mocker.patch("app.domains.tiers.routes.TierService.list_tiers")

    mock_list.return_value = [
        {
            "id": "tier-123",
            "name": "Pro",
            "price": 2000,
            "message_limit": 1000,
            "image_limit": 100,
            "research_limit": 50,
            "document_limit": 100,
            "model_access": ["gpt-4", "claude-3"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    ]

    response = client.get("/tiers/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_list.assert_called_once()


def test_get_tier_by_id_route(mocker: MockerFixture):
    mock_get = mocker.patch("app.domains.tiers.routes.TierService.get_tier_by_id")

    mock_get.return_value = {
        "id": "tier-123",
        "name": "Pro",
        "price": 2000,
        "message_limit": 1000,
        "image_limit": 100,
        "research_limit": 50,
        "document_limit": 100,
        "model_access": ["gpt-4", "claude-3"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    response = client.get("/tiers/tier-123")

    assert response.status_code == 200
    assert response.json()["name"] == "Pro"
    mock_get.assert_called_once()


def test_update_tier_route(mocker: MockerFixture):
    mock_update = mocker.patch("app.domains.tiers.routes.TierService.update_tier")

    mock_update.return_value = {
        "id": "tier-123",
        "name": "Pro",
        "price": 2500,
        "message_limit": 1000,
        "image_limit": 100,
        "research_limit": 50,
        "document_limit": 100,
        "model_access": ["gpt-4", "claude-3"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    payload = {"price": 2500}

    response = client.patch("/tiers/tier-123", json=payload)

    assert response.status_code == 202
    assert response.json()["price"] == 2500
    mock_update.assert_called_once()


def test_delete_tier_route(mocker: MockerFixture):
    mock_delete = mocker.patch("app.domains.tiers.routes.TierService.delete_tier")

    response = client.delete("/tiers/tier-123")

    assert response.status_code == 204
    mock_delete.assert_called_once()
