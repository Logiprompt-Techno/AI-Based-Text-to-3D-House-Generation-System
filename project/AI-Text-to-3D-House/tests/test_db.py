import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.database import Base
from backend.db.models import User, Design
from sqlalchemy.exc import IntegrityError

# Use an in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

def test_database_initializes_successfully(db_session):
    # If tables are created, querying them shouldn't throw operational errors
    assert db_session.query(User).count() == 0

def test_user_creation_and_retrieval(db_session):
    new_user = User(email="test@example.com", password_hash="hashedpassword")
    db_session.add(new_user)
    db_session.commit()

    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.id is not None
    assert user.created_at is not None

def test_email_uniqueness(db_session):
    user1 = User(email="unique@example.com", password_hash="hash1")
    db_session.add(user1)
    db_session.commit()

    user2 = User(email="unique@example.com", password_hash="hash2")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_design_creation_and_user_relationship(db_session):
    # Create user
    user = User(email="designer@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    # Create design
    design = Design(
        user_id=user.id,
        name="My Cool House",
        prompt="Modern house",
        requirements_json={"bedrooms": 3},
        layout_json={"boxes": []},
        floorplan_json={"rooms": []},
        house3d_json={"objects": []}
    )
    db_session.add(design)
    db_session.commit()

    # Retrieve design
    fetched_design = db_session.query(Design).filter(Design.name == "My Cool House").first()
    assert fetched_design is not None
    assert fetched_design.prompt == "Modern house"
    
    # Test relationship
    assert fetched_design.user.email == "designer@example.com"
    
    # Test reverse relationship
    assert len(user.designs) == 1
    assert user.designs[0].name == "My Cool House"
