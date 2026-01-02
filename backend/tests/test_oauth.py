import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import get_db, Base
from src.auth.oauth import OAuthService
from src.config import settings

# Setup test DB (same as test_api.py)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_oauth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_generate_state():
    state1 = OAuthService.generate_state()
    state2 = OAuthService.generate_state()
    assert len(state1) > 10
    assert state1 != state2

def test_google_url_generation():
    # Mock settings
    with patch.object(settings, 'GOOGLE_CLIENT_ID', 'mock_id'):
        with patch.object(settings, 'GOOGLE_REDIRECT_URI', 'http://localhost/cb'):
            url = OAuthService.get_google_auth_url("test_state")
            assert "https://accounts.google.com/o/oauth2/v2/auth" in url
            assert "client_id=mock_id" in url
            assert "state=test_state" in url

def test_microsoft_url_generation():
    with patch.object(settings, 'MS_CLIENT_ID', 'mock_id'):
        with patch.object(settings, 'MICROSOFT_REDIRECT_URI', 'http://localhost/cb'):
            url = OAuthService.get_microsoft_auth_url("test_state")
            assert "https://login.microsoftonline.com" in url
            assert "client_id=mock_id" in url
            assert "state=test_state" in url

def test_oauth_start_endpoint():
    # Test that start endpoint redirects and sets cookie
    with patch.object(OAuthService, 'get_google_auth_url', return_value="https://google.com/auth"):
        response = client.get("/api/auth/oauth/google/start", allow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "https://google.com/auth"
        assert "oauth_state" in response.cookies

def test_oauth_callback_invalid_state():
    # Test callback with mismatching state
    response = client.get(
        "/api/auth/oauth/google/callback?code=123&state=invalid",
        cookies={"oauth_state": "valid_state"},
        allow_redirects=False
    )
    # Should redirect to login with error
    assert response.status_code == 307
    assert "login?error=invalid_state" in response.headers["location"]
