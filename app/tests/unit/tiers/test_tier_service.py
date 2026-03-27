import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime, timezone

from app.domains.tiers.service import (
    TierService,
    TierConflictException,
    TierNotFoundException,
)
from app.domains.tiers.schemas import TierCreate, TierUpdate
from app.domains.tiers.models import Tiers


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def fake_tier():
    return Tiers(
        id="tier-123",
        name="Pro",
        price=2000,
        message_limit=1000,
        image_limit=100,
        research_limit=50,
        document_limit=100,
        model_access=["gpt-4", "claude-3"],
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_create_tier_success(mock_db_session, mocker):
    tier_data = TierCreate(
        name="Pro",
        price=2000,
        message_limit=1000,
        image_limit=100,
        research_limit=50,
        document_limit=100,
        model_access=["gpt-4", "claude-3"],
        is_active=True,
    )

    def fake_db_refresh(instance):
        instance.id = "tier-123"
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db_session.refresh.side_effect = fake_db_refresh

    result = TierService.create_tier(mock_db_session, tier_data)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert result.id == "tier-123"


def test_create_tier_conflict(mock_db_session):
    tier_data = TierCreate(
        name="Pro",
        price=2000,
        message_limit=1000,
        image_limit=100,
        research_limit=50,
        document_limit=100,
        model_access=["gpt-4", "claude-3"],
        is_active=True,
    )

    mock_db_session.commit.side_effect = IntegrityError("", "", "")

    with pytest.raises(HTTPException) as exc_info:
        TierService.create_tier(mock_db_session, tier_data)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Tier with this name already exists"
    mock_db_session.rollback.assert_called_once()


def test_list_tiers(mock_db_session, fake_tier):
    mock_db_session.query.return_value.all.return_value = [fake_tier]

    result = TierService.list_tiers(mock_db_session)

    assert len(result) == 1
    mock_db_session.query.assert_called_once()


def test_get_tier_by_id_success(mock_db_session, fake_tier):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_tier
    )

    result = TierService.get_tier_by_id(mock_db_session, "tier-123")

    assert result.id == "tier-123"
    assert result.name == "Pro"


def test_get_tier_by_id_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        TierService.get_tier_by_id(mock_db_session, "nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Tier not found"


def test_update_tier_success(mock_db_session, fake_tier):
    update_data = TierUpdate(price=2500)

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_tier
    )

    result = TierService.update_tier(mock_db_session, "tier-123", update_data)

    assert result.price == 2500
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_update_tier_not_found(mock_db_session):
    update_data = TierUpdate(price=2500)

    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        TierService.update_tier(mock_db_session, "nonexistent", update_data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Tier not found"


def test_update_tier_conflict(mock_db_session, fake_tier):
    update_data = TierUpdate(name="Enterprise")

    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_tier
    )
    mock_db_session.commit.side_effect = IntegrityError("", "", "")

    with pytest.raises(HTTPException) as exc_info:
        TierService.update_tier(mock_db_session, "tier-123", update_data)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Tier with this name already exists"
    mock_db_session.rollback.assert_called_once()


def test_delete_tier_success(mock_db_session, fake_tier):
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        fake_tier
    )

    TierService.delete_tier(mock_db_session, "tier-123")

    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_delete_tier_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        TierService.delete_tier(mock_db_session, "nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Tier not found"
