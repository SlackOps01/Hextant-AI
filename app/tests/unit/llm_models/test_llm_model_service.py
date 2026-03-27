import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime, timezone

from app.domains.llm_models.service import (
    LanguageModelService,
    LanguageModelConflictException,
    LanguageModelNotFoundException,
)
from app.domains.llm_models.schemas import LanguageModelCreate, LanguageModelUpdate
from app.domains.llm_models.models import LanguageModels, ModelType, ModelModality


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def fake_language_model():
    return LanguageModels(
        id="model-123",
        display_name="GPT-4",
        model_type=ModelType.TEXT,
        modality=ModelModality.TEXT,
        context_length=8192,
        provider="OpenAI",
        input_token_price=30,
        output_token_price=60,
        api_identifier="gpt-4",
        adapter="generic",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_add_language_model_success(mock_db_session, mocker):
    model_data = LanguageModelCreate(
        display_name="GPT-4",
        model_type=ModelType.TEXT,
        modality=ModelModality.TEXT,
        context_length=8192,
        provider="OpenAI",
        input_token_price=30,
        output_token_price=60,
        api_identifier="gpt-4",
        adapter="generic",
    )

    def fake_db_refresh(instance):
        instance.id = "model-123"
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db_session.refresh.side_effect = fake_db_refresh

    result = LanguageModelService.add_language_model(mock_db_session, model_data)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert result.id == "model-123"


def test_add_language_model_conflict(mock_db_session, mocker):
    model_data = LanguageModelCreate(
        display_name="GPT-4",
        model_type=ModelType.TEXT,
        modality=ModelModality.TEXT,
        context_length=8192,
        provider="OpenAI",
        input_token_price=30,
        output_token_price=60,
        api_identifier="gpt-4",
        adapter="generic",
    )

    mock_db_session.commit.side_effect = IntegrityError("", "", "")

    with pytest.raises(HTTPException) as exc_info:
        LanguageModelService.add_language_model(mock_db_session, model_data)

    assert exc_info.value.status_code == 409
    assert (
        exc_info.value.detail
        == "Language model with this api_identifier already exists"
    )
    mock_db_session.rollback.assert_called_once()


def test_list_language_models(mock_db_session, fake_language_model):
    mock_db_session.query.return_value.all.return_value = [fake_language_model]

    result = LanguageModelService.list_language_models(mock_db_session)

    assert len(result) == 1
    mock_db_session.query.assert_called_once()


def test_update_language_model_success(mock_db_session, fake_language_model):
    update_data = LanguageModelUpdate(display_name="GPT-4 Turbo")

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_language_model
    )

    result = LanguageModelService.update_language_model(
        mock_db_session, "model-123", update_data
    )

    assert result.display_name == "GPT-4 Turbo"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_update_language_model_not_found(mock_db_session):
    update_data = LanguageModelUpdate(display_name="GPT-4 Turbo")

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        LanguageModelService.update_language_model(
            mock_db_session, "nonexistent", update_data
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Language model not found"


def test_delete_language_model_success(mock_db_session, fake_language_model):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_language_model
    )

    LanguageModelService.delete_language_model(mock_db_session, "model-123")

    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_delete_language_model_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        LanguageModelService.delete_language_model(mock_db_session, "nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Language model not found"
