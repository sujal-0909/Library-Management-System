import pytest
from src.models import db
from src.models.member import Member

def test_login_success(client, init_database):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'password'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['member']['username'] == 'admin'
    assert data['member']['is_active'] is True

def test_login_invalid_credentials(client, init_database):
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'Invalid username or password' in response.get_json()['error']

def test_register_member(client, test_app):
    response = client.post('/api/auth/register', json={
        'first_name': 'New',
        'last_name': 'User',
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'testpassword123',
        'phone': '1112223334',
        'address': 'Test Address 3'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'Member registered successfully' in data['message']
    
    with test_app.app_context():
        member = Member.query.filter_by(username='newuser').first()
        assert member is not None
        assert member.email == 'newuser@example.com'

def test_get_profile(client, init_database, user_token):
    response = client.get('/api/auth/profile', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['profile']['username'] == 'testuser'
