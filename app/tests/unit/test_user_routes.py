# test_user_routes.py
from datetime import timezone
from datetime import datetime
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.domains.users.routes import router # Import your router
from app.core.deps import get_db
from app.domains.users.security import require_admin, require_owner_or_admin
from app.domains.users.schemas import UserResponse

# 1. Create a dummy FastAPI app and attach your router
app = FastAPI()
app.include_router(router)

client = TestClient(app)

# 2. Setup Dependency Overrides
# We bypass the DB and Auth so we don't have to generate real JWT tokens for testing
def override_get_db():
    yield "mocked_db"

def override_require_admin():
    return {"user_id": "admin_123", "role": "admin"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_admin] = override_require_admin
app.dependency_overrides[require_owner_or_admin] = override_require_admin


def test_register_user_route(mocker):
    # Setup: Mock the Service layer so we don't actually hit a database
    mock_create = mocker.patch(
        "app.domains.users.routes.UserService.create_user",
        return_value=UserResponse(
            id="user_id",
            email="lanre@test.com",
            username="lanre",
            role="user",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    )

    payload = {
        "id": "user_id",
        "email": "lanre@test.com", 
        "username": "lanre", 
        "password": "password123",
        "role": "user",
        "created_at": str(datetime.now(timezone.utc)),
        "updated_at": str(datetime.now(timezone.utc))
    }

    response = client.post("/users/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == "lanre@test.com"
    mock_create.assert_called_once()

def test_list_users_route(mocker):
    mocker.patch(
        "app.domains.users.routes.UserService.list_users",
        return_value=[
            UserResponse(
                id="user_id",
                email="lanre@test.com",
                username="lanre",
                role="user",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        ]
    )

    response = client.get("/users")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["username"] == "lanre" 