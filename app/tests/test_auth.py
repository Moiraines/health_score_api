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
async def test_register_user():
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'full_name': 'Test User'
        }
    )
    assert response.status_code == 200
    assert response.json()['username'] == 'testuser'
    assert response.json()['email'] == 'testuser@example.com'

@pytest.mark.asyncio
async def test_register_user_duplicate_username():
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser',
            'email': 'testuser2@example.com',
            'password': 'testpassword2',
            'full_name': 'Test User 2'
        }
    )
    assert response.status_code == 400
    assert 'Username already registered' in response.json()['detail']

@pytest.mark.asyncio
async def test_login_user():
    response = client.post(
        '/api/v1/token',
        data={'username': 'testuser', 'password': 'testpassword'}
    )
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()
    assert response.json()['token_type'] == 'bearer'

@pytest.mark.asyncio
async def test_login_user_invalid_credentials():
    response = client.post(
        '/api/v1/token',
        data={'username': 'testuser', 'password': 'wrongpassword'}
    )
    assert response.status_code == 401
    assert 'Incorrect username or password' in response.json()['detail']

@pytest.mark.asyncio
async def test_refresh_token():
    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser', 'password': 'testpassword'}
    )
    refresh_token = login_response.json()['refresh_token']

    response = client.post(
        '/api/v1/refresh-token',
        json={'refresh_token': refresh_token}
    )
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()

@pytest.mark.asyncio
async def test_refresh_token_invalid():
    response = client.post(
        '/api/v1/refresh-token',
        json={'refresh_token': 'invalid_token'}
    )
    assert response.status_code == 401
    assert 'Invalid refresh token' in response.json()['detail']
