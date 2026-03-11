import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.main import app
from src.models import db
from src.models.member import Member
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

@pytest.fixture
def test_app():
    """Create and configure a new app instance for each test."""
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture
def init_database(test_app):
    """Initialize test database with a test user"""
    with test_app.app_context():
        # Create an admin user for authenticated requests
        admin_member = Member(
            first_name="Admin",
            last_name="User",
            username="admin",
            email="admin@example.com",
            phone="1234567890",
            address="Test Address"
        )
        admin_member.set_password("password")
        db.session.add(admin_member)
        
        # Create a regular user
        regular_member = Member(
            first_name="Test",
            last_name="User",
            username="testuser",
            email="test@example.com",
            phone="0987654321",
            address="Test Address 2"
        )
        regular_member.set_password("password")
        db.session.add(regular_member)
        
        db.session.commit()
        
        # Keep instances attached for access in tests
        db.session.refresh(admin_member)
        db.session.refresh(regular_member)
        
        yield {
            "admin_id": admin_member.member_id,
            "user_id": regular_member.member_id
        }

@pytest.fixture
def admin_token(test_app, init_database):
    """Return an access token for the admin test user."""
    with test_app.app_context():
        return create_access_token(identity=init_database['admin_id'])

@pytest.fixture
def user_token(test_app, init_database):
    """Return an access token for the regular test user."""
    with test_app.app_context():
        return create_access_token(identity=init_database['user_id'])
