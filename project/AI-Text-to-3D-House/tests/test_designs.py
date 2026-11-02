import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import backend.db.models

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

@pytest.fixture
def auth_headers_user1():
    client.post("/api/auth/register", json={"email": "user1@example.com", "password": "pass"})
    res = client.post("/api/auth/login", json={"email": "user1@example.com", "password": "pass"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

@pytest.fixture
def auth_headers_user2():
    client.post("/api/auth/register", json={"email": "user2@example.com", "password": "pass"})
    res = client.post("/api/auth/login", json={"email": "user2@example.com", "password": "pass"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_create_design_unauthenticated():
    res = client.post("/api/designs", json={"name": "test", "prompt": "test prompt"})
    assert res.status_code in [401, 403]

def test_create_and_get_design(auth_headers_user1):
    payload = {
        "name": "My Dream House",
        "prompt": "Modern villa",
        "requirements_json": {"rooms": 4},
        "layout_json": {"size": 200},
        "floorplan_json": {"doors": 2},
        "house3d_json": {"vertices": 500}
    }
    res = client.post("/api/designs", json=payload, headers=auth_headers_user1)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "My Dream House"
    assert data["requirements_json"] == {"rooms": 4}
    assert "id" in data
    
    design_id = data["id"]
    
    # Get by ID
    res = client.get(f"/api/designs/{design_id}", headers=auth_headers_user1)
    assert res.status_code == 200
    assert res.json()["id"] == design_id

def test_list_designs(auth_headers_user1):
    # Create two designs
    client.post("/api/designs", json={"name": "D1", "prompt": "P1"}, headers=auth_headers_user1)
    client.post("/api/designs", json={"name": "D2", "prompt": "P2"}, headers=auth_headers_user1)
    
    res = client.get("/api/designs", headers=auth_headers_user1)
    assert res.status_code == 200
    assert len(res.json()) == 2
    # Ensure newest first
    assert res.json()[0]["name"] == "D2"
    assert res.json()[1]["name"] == "D1"

def test_cross_user_isolation(auth_headers_user1, auth_headers_user2):
    # User 1 creates design
    res1 = client.post("/api/designs", json={"name": "U1 Design", "prompt": "P1"}, headers=auth_headers_user1)
    design_id = res1.json()["id"]
    
    # User 2 tries to get User 1's design
    res2 = client.get(f"/api/designs/{design_id}", headers=auth_headers_user2)
    assert res2.status_code == 404
    
    # User 2 tries to update User 1's design
    res2_put = client.put(f"/api/designs/{design_id}", json={"name": "Hacked"}, headers=auth_headers_user2)
    assert res2_put.status_code == 404
    
    # User 2 tries to delete User 1's design
    res2_del = client.delete(f"/api/designs/{design_id}", headers=auth_headers_user2)
    assert res2_del.status_code == 404
    
    # User 2 lists designs, should be empty
    res2_list = client.get("/api/designs", headers=auth_headers_user2)
    assert len(res2_list.json()) == 0

def test_update_design(auth_headers_user1):
    res = client.post("/api/designs", json={"name": "Original", "prompt": "P"}, headers=auth_headers_user1)
    d_id = res.json()["id"]
    
    res_put = client.put(f"/api/designs/{d_id}", json={"name": "Updated"}, headers=auth_headers_user1)
    assert res_put.status_code == 200
    assert res_put.json()["name"] == "Updated"
    assert res_put.json()["prompt"] == "P"  # unchanged
    
def test_delete_design(auth_headers_user1):
    res = client.post("/api/designs", json={"name": "To Delete", "prompt": "P"}, headers=auth_headers_user1)
    d_id = res.json()["id"]
    
    res_del = client.delete(f"/api/designs/{d_id}", headers=auth_headers_user1)
    assert res_del.status_code == 204
    
    res_get = client.get(f"/api/designs/{d_id}", headers=auth_headers_user1)
    assert res_get.status_code == 404

def test_invalid_design_id(auth_headers_user1):
    res = client.get("/api/designs/nonexistent-id", headers=auth_headers_user1)
    assert res.status_code == 404
