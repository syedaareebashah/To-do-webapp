"""
Conftest for pytest - shared fixtures and configuration.
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-minimum-32-chars"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-only-minimum-32-chars"
os.environ["JWT_EXPIRATION_HOURS"] = "1"

from app.main import app
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    """Create a test user and return authentication headers."""
    # Create test user
    signup_response = client.post(
        "/auth/signup",
        json={"email": "testuser@example.com", "password": "Password123"}
    )

    token = signup_response.json()["token"]
    user_id = signup_response.json()["user"]["user_id"]

    return {
        "token": f"Bearer {token}",
        "user_id": user_id
    }
