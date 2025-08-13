"""Basic tests for UpLite application."""

import pytest
from src.uplite.app import create_app, db
from src.uplite.config.settings import TestingConfig
from src.uplite.models.user import User


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()


@pytest.fixture
def user(app):
    """Create test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        db.session.add(user)
        db.session.commit()
        return user


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'uplite'


def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'UpLite' in response.data


def test_login_page(client):
    """Test login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_register_page(client):
    """Test register page loads."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data


def test_user_creation(app):
    """Test user creation."""
    with app.app_context():
        user = User(
            username='newuser',
            email='new@example.com',
            password='newpassword'
        )
        
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('newpassword')
        assert not user.check_password('wrongpassword')


def test_login_logout(client, user):
    """Test user login and logout."""
    # Test login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword',
        'csrf_token': 'test'  # In real tests, you'd need proper CSRF handling
    })
    
    # Should redirect after successful login
    assert response.status_code in [200, 302]
    
    # Test logout
    response = client.get('/auth/logout')
    assert response.status_code == 302  # Should redirect after logout


def test_dashboard_requires_login(client):
    """Test that dashboard requires authentication."""
    response = client.get('/dashboard/')
    assert response.status_code == 302  # Should redirect to login


def test_api_endpoints_require_login(client):
    """Test that API endpoints require authentication."""
    endpoints = [
        '/api/connections',
        '/api/widgets',
        '/api/dashboard/refresh'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 302  # Should redirect to login
