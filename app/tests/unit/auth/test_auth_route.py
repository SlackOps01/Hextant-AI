from redis.asyncio import Redis
from pytest_mock import MockerFixture
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.domains.auth.routes import router
from unittest.mock import AsyncMock


app = FastAPI()

app.include_router(router)

client = TestClient(app)


def test_login(mocker: MockerFixture):
    mock_login = mocker.patch("app.domains.auth.routes.AuthService.login")

    mock_login.return_value = {"access_token": "access-jwt", "token_type": "bearer"}

    payload = {"username": "lanre", "password": "password1234"}

    response = client.post("/auth/login", data=payload)

    assert response.status_code == 200
    assert response.json()["access_token"] == "access-jwt"
    mock_login.assert_called_once()


def test_logout(mocker: MockerFixture):
    mock_logout = mocker.patch("app.domains.auth.routes.AuthService.logout")
    mock_logout.return_value = {"status": "revoked"}
    app.state.redis_client = AsyncMock(spec=Redis)
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["status"] == "revoked"
    mock_logout.assert_called_once()


def test_refresh(mocker: MockerFixture):
    mock_refresh = mocker.patch("app.domains.auth.routes.AuthService.refresh")
    mock_refresh.return_value = {"access_token": "access_token", "token_type": "bearer"}

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    mock_refresh.assert_awaited_once()
