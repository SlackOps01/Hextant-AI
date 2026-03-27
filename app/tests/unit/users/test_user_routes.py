from datetime import timezone
from datetime import datetime
from pytest_mock import MockerFixture

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.domains.users.routes import router
from app.core.deps import get_db
from app.domains.users.security import require_admin, require_owner_or_admin, Role

app = FastAPI()

app.include_router(router)

client = TestClient(app)


def override_get_db():
    yield MagicMock(spec=Session)


def override_require_admin():
    return {"id": "admin_123", "role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_owner_or_admin] = override_require_admin
app.dependency_overrides[require_admin] = override_require_admin


def test_user_register_route(mocker: MockerFixture):
    mock_create = mocker.patch("app.domains.users.routes.UserService.create_user")

    mock_create.return_value = {
        "id": "123",
        "email": "email@mail.com",
        "username": "lanre",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "role": Role.USER.value,
    }

    payload = {"username": "lanre", "email": "email@mail.com", "password": "12345678"}

    response = client.post("/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["username"] == "lanre"
    mock_create.assert_called_once()


def test_list_users_route(mocker: MockerFixture):
    mock_list = mocker.patch("app.domains.users.routes.UserService.list_users")

    mock_list.return_value = [
        {
            "id": "123",
            "email": "email@mail.com",
            "username": "lanre",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "role": Role.USER.value,
        }
    ]

    response = client.get("/users")

    assert response.status_code == 200


def test_delete_user(mocker: MockerFixture):
    mock_delete = mocker.patch("app.domains.users.routes.UserService.delete_user")

    mock_delete.return_value = {"status": "success"}

    result = client.delete("/users/123")

    assert result.status_code == 204
