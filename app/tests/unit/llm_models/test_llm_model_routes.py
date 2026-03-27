from datetime import datetime, timezone
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.domains.llm_models.routes import router
from app.domains.llm_models.models import ModelType, ModelModality
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


def test_add_language_model_route(mocker: MockerFixture):
    mock_create = mocker.patch(
        "app.domains.llm_models.routes.LanguageModelService.add_language_model"
    )

    mock_create.return_value = {
        "id": "model-123",
        "display_name": "GPT-4",
        "model_type": ModelType.TEXT.value,
        "modality": ModelModality.TEXT.value,
        "context_length": 8192,
        "provider": "OpenAI",
        "input_token_price": 30,
        "output_token_price": 60,
        "api_identifier": "gpt-4",
        "adapter": "generic",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    payload = {
        "display_name": "GPT-4",
        "model_type": "text",
        "modality": "text",
        "context_length": 8192,
        "provider": "OpenAI",
        "input_token_price": 30,
        "output_token_price": 60,
        "api_identifier": "gpt-4",
        "adapter": "generic",
    }

    response = client.post("/llm-models/", json=payload)

    assert response.status_code == 201
    assert response.json()["api_identifier"] == "gpt-4"
    mock_create.assert_called_once()


def test_list_language_models_route(mocker: MockerFixture):
    mock_list = mocker.patch(
        "app.domains.llm_models.routes.LanguageModelService.list_language_models"
    )

    mock_list.return_value = [
        {
            "id": "model-123",
            "display_name": "GPT-4",
            "model_type": ModelType.TEXT.value,
            "modality": ModelModality.TEXT.value,
            "context_length": 8192,
            "provider": "OpenAI",
            "input_token_price": 30,
            "output_token_price": 60,
            "api_identifier": "gpt-4",
            "adapter": "generic",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    ]

    response = client.get("/llm-models/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_list.assert_called_once()


def test_update_language_model_route(mocker: MockerFixture):
    mock_update = mocker.patch(
        "app.domains.llm_models.routes.LanguageModelService.update_language_model"
    )

    mock_update.return_value = {
        "id": "model-123",
        "display_name": "GPT-4 Turbo",
        "model_type": ModelType.TEXT.value,
        "modality": ModelModality.TEXT.value,
        "context_length": 8192,
        "provider": "OpenAI",
        "input_token_price": 30,
        "output_token_price": 60,
        "api_identifier": "gpt-4",
        "adapter": "generic",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    payload = {"display_name": "GPT-4 Turbo"}

    response = client.patch("/llm-models/model-123", json=payload)

    assert response.status_code == 202
    assert response.json()["display_name"] == "GPT-4 Turbo"
    mock_update.assert_called_once()


def test_delete_language_model_route(mocker: MockerFixture):
    mock_delete = mocker.patch(
        "app.domains.llm_models.routes.LanguageModelService.delete_language_model"
    )

    response = client.delete("/llm-models/model-123")

    assert response.status_code == 204
    mock_delete.assert_called_once()
