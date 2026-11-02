import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.db.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
import jwt
from sqlalchemy import create_engine
import backend.db.models  # Required for Base.metadata to know about tables

from sqlalchemy.pool import StaticPool

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()

def test_successful_registration():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data

def test_duplicate_registration_rejection():
    # Register first time
    client.post("/api/auth/register", json={"email": "duplicate@example.com", "password": "pass"})
    # Register second time
    response = client.post("/api/auth/register", json={"email": "duplicate@example.com", "password": "pass"})
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_successful_login():
    client.post("/api/auth/register", json={"email": "login@example.com", "password": "mypassword"})
    response = client.post("/api/auth/login", json={"email": "login@example.com", "password": "mypassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_password_rejection():
    client.post("/api/auth/register", json={"email": "invalid@example.com", "password": "mypassword"})
    response = client.post("/api/auth/login", json={"email": "invalid@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_unauthenticated_me_rejection():
    response = client.get("/api/auth/me")
    assert response.status_code == 403 or response.status_code == 401

def test_authenticated_me():
    # Register & Login
    client.post("/api/auth/register", json={"email": "me@example.com", "password": "mypassword"})
    login_response = client.post("/api/auth/login", json={"email": "me@example.com", "password": "mypassword"})
    token = login_response.json()["access_token"]
    
    # Get Me
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert "id" in data

def test_invalid_token_rejection():
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer fake.jwt.token"})
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]
