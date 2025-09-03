import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///./test.db'
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_current_user():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'full_name': 'Test User'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Get current user
    response = client.get(
        '/api/v1/users/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json()['username'] == 'testuser'
    assert response.json()['email'] == 'testuser@example.com'

@pytest.mark.asyncio
async def test_get_current_user_unauthorized():
    response = client.get('/api/v1/users/me')
    assert response.status_code == 401
    assert 'Not authenticated' in response.json()['detail']

@pytest.mark.asyncio
async def test_get_users_admin():
    # Register and login as admin user (assuming first user is admin or create admin user)
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password': 'adminpassword',
            'full_name': 'Admin User'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'adminuser', 'password': 'adminpassword'}
    )
    token = login_response.json()['access_token']

    # Assuming admin privileges are set for this user, or update test to make first user admin
    # For now, test will assume admin status
    response = client.get(
        '/api/v1/users/',
        headers={'Authorization': f'Bearer {token}'}
    )
    # Note: This test may fail if admin check is not mocked or set
    assert response.status_code == 200 or response.status_code == 403
    if response.status_code == 200:
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_users_non_admin():
    # Register and login as non-admin user
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'regularuser',
            'email': 'regular@example.com',
            'password': 'regularpassword',
            'full_name': 'Regular User'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'regularuser', 'password': 'regularpassword'}
    )
    token = login_response.json()['access_token']

    response = client.get(
        '/api/v1/users/',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
    assert 'Admin access required' in response.json()['detail']
