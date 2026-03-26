import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import Request, Response, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pytest_mock import MockerFixture
from app.domains.auth.service import AuthService

# IMPORTANT: Change this to the actual path where your AuthService lives!
SERVICE_PATH = "app.domains.auth.service" 

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = "user-123"
    user.username = "lanre"
    user.email = "lanre@test.com"
    user.password = "hashed_password"
    user.role = "user"
    return user

@pytest.fixture
def form_data():
    form = MagicMock(spec=OAuth2PasswordRequestForm)
    form.username = "lanre@test.com"
    form.password = "MySecretPassword"
    return form

@pytest.fixture
def mock_redis():
    # Because Redis methods are awaited in your code, we MUST use AsyncMock!
    return AsyncMock()

@pytest.fixture
def mock_request():
    req = MagicMock(spec=Request)
    # Simulate a user sending a request with a valid refresh cookie
    req.cookies.get.return_value = "existing-refresh-token"
    return req

@pytest.fixture
def mock_response():
    return MagicMock(spec=Response)

@pytest.fixture
def fake_token_data():
    # A fake version of what verify_token returns
    token_data = MagicMock()
    token_data.jti = "jti-123"
    token_data.id = "user-1"
    token_data.role = "user"
    token_data.exp = 9999999999
    return token_data

@pytest.fixture
def fake_auth_session():
    # A fake AuthSessions database model
    session = MagicMock()
    session.refresh_token_jti = "jti-123"
    session.is_revoked = False
    return session

@pytest.fixture
def setup_async_mocks(mocker: MockerFixture):
    """A helper fixture to mock the things both tests share."""
    # 1. THE MAGIC TRICK for run_in_threadpool:
    # We tell it to just instantly execute the lambda function we pass to it!
    async def fake_run_in_threadpool(func, *args, **kwargs):
        return func(*args, **kwargs)
    mocker.patch(f"{SERVICE_PATH}.run_in_threadpool", side_effect=fake_run_in_threadpool)

    # 2. Mock token verification
    mock_verify = mocker.patch(f"{SERVICE_PATH}.verify_token")
    
    # 3. Mock Redis revocation checks
    mock_is_revoked = mocker.patch(f"{SERVICE_PATH}.is_token_revoked", return_value=False)
    mock_revoke_tokens = mocker.patch(f"{SERVICE_PATH}.revoke_tokens")
    
    return mock_verify, mock_is_revoked, mock_revoke_tokens

def test_login_success(
    mock_db, fake_user, mock_request, mock_response, form_data, mocker
):
    # 1. SETUP DB
    mock_db.query.return_value.filter.return_value.first.return_value = fake_user

    # 2. PATCH ALL UTILITIES IN THE AUTH SERVICE NAMESPACE
    # Notice we patch them exactly where AuthService imports them!
    mock_verify = mocker.patch("app.domains.auth.service.verify_password", return_value=True)
    mock_uuid7 = mocker.patch("app.domains.auth.service.uuid7", return_value="mocked-jti-uuid")
    mock_create_access = mocker.patch("app.domains.auth.service.create_access_token", return_value="access-jwt")
    mock_create_refresh = mocker.patch("app.domains.auth.service.create_refresh_token", return_value="refresh-jwt")
    mock_set_cookie = mocker.patch("app.domains.auth.service.set_refresh_cookie")
    
    # Mock the user_agent_parser
    mocker.patch("app.domains.auth.service.user_agent_parser.ParseOS", return_value={"family": "Windows"})
    mocker.patch("app.domains.auth.service.user_agent_parser.ParseDevice", return_value={"family": "PC"})

    # 3. EXECUTE
    result = AuthService.login(
        request=mock_request, 
        response=mock_response, 
        db=mock_db, 
        form_data=form_data
    )

    # 4. ASSERTIONS
    mock_verify.assert_called_once_with("MySecretPassword", "hashed_password")
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    
    # Verify the AuthSession was created with the right parsed data
    added_session = mock_db.add.call_args[0][0]
    assert added_session.user_id == "user-123"
    assert added_session.device_os == "Windows"
    assert added_session.refresh_token_jti == "mocked-jti-uuid"

    # Verify cookie and return values
    mock_set_cookie.assert_called_once_with(mock_response, "refresh-jwt")
    assert result == {
        "access_token": "access-jwt",
        "token_type": "bearer"
    }

@pytest.mark.asyncio
async def test_logout_success(
    mock_db, mock_redis, mock_request, mock_response, fake_token_data, 
    fake_auth_session, setup_async_mocks
):
    mock_verify, mock_is_revoked, mock_revoke_tokens = setup_async_mocks
    mock_verify.return_value = fake_token_data
    
    # Setup DB to return the session
    mock_db.query.return_value.filter.return_value.first.return_value = fake_auth_session

    # Execute (Remember to await it!)
    # Import your actual service
    result = await AuthService.logout(mock_request, mock_response, mock_db, mock_redis)

    # Assertions
    assert fake_auth_session.is_revoked is True
    mock_db.commit.assert_called_once()
    mock_revoke_tokens.assert_called_once_with(mock_redis, "jti-123", 9999999999)
    mock_response.delete_cookie.assert_called_once()
    assert result == {"status": "revoked"}  


@pytest.mark.asyncio
async def test_refresh_success(
    mock_db, mock_redis, mock_request, mock_response, fake_token_data, 
    fake_auth_session, setup_async_mocks, mocker: MockerFixture
):
    mock_verify, mock_is_revoked, mock_revoke_tokens = setup_async_mocks
    mock_verify.return_value = fake_token_data
    
    # Setup DB to return the active session
    mock_db.query.return_value.filter.return_value.first.return_value = fake_auth_session

    # Mock the new token generators and cookie setter
    mocker.patch(f"{SERVICE_PATH}.uuid7", return_value="new-jti-456")
    mocker.patch(f"{SERVICE_PATH}.create_refresh_token", return_value="new-refresh-jwt")
    mocker.patch(f"{SERVICE_PATH}.create_access_token", return_value="new-access-jwt")
    mock_set_cookie = mocker.patch(f"{SERVICE_PATH}.set_refresh_cookie")

    # Execute
    result = await AuthService.refresh(mock_request, mock_response, mock_db, mock_redis)

    # Assertions
    mock_revoke_tokens.assert_called_once_with(mock_redis, "jti-123", 9999999999) # Did we kill the old token?
    assert fake_auth_session.refresh_token_jti == "new-jti-456"                   # Did we update the DB session?
    mock_db.commit.assert_called_once()                                           # Did we save it?
    mock_set_cookie.assert_called_once_with(mock_response, "new-refresh-jwt")     # Did we set the new cookie?
    
    assert result == {"access_token": "new-access-jwt", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_refresh_fails_if_already_revoked_in_db(
    mock_db, mock_redis, mock_request, mock_response, fake_token_data, 
    fake_auth_session, setup_async_mocks
):
    mock_verify, _, _ = setup_async_mocks
    mock_verify.return_value = fake_token_data
    
    # Setup the DB session, but mark it as ALREADY REVOKED!
    fake_auth_session.is_revoked = True
    mock_db.query.return_value.filter.return_value.first.return_value = fake_auth_session

    from app.domains.auth.service import AuthService, InvalidCredentialException
    
    with pytest.raises(HTTPException):
        await AuthService.refresh(mock_request, mock_response, mock_db, mock_redis)