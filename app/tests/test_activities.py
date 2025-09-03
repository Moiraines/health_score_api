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
async def test_create_activity():
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

    # Then create activity
    response = client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Running',
            'duration_minutes': 30,
            'distance_km': 5.0,
            'calories_burned': 300.0,
            'notes': 'Morning run'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json()['activity_type'] == 'Running'
    assert response.json()['duration_minutes'] == 30

@pytest.mark.asyncio
async def test_create_activity_unauthorized():
    response = client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Cycling',
            'duration_minutes': 45
        }
    )
    assert response.status_code == 401
    assert 'Not authenticated' in response.json()['detail']

@pytest.mark.asyncio
async def test_get_activities():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'testpassword',
            'full_name': 'Test User 2'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser2', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Create an activity to ensure there is at least one
    client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Swimming',
            'duration_minutes': 60,
            'distance_km': 2.0,
            'calories_burned': 400.0
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    # Get activities
    response = client.get(
        '/api/v1/activities/',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_activities_unauthorized():
    response = client.get('/api/v1/activities/')
    assert response.status_code == 401
    assert 'Not authenticated' in response.json()['detail']

@pytest.mark.asyncio
async def test_get_activity():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser3',
            'email': 'testuser3@example.com',
            'password': 'testpassword',
            'full_name': 'Test User 3'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser3', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Create an activity
    create_response = client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Yoga',
            'duration_minutes': 45,
            'calories_burned': 200.0
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    activity_id = create_response.json()['id']

    # Get specific activity
    response = client.get(
        f'/api/v1/activities/{activity_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json()['id'] == activity_id
    assert response.json()['activity_type'] == 'Yoga'

@pytest.mark.asyncio
async def test_get_activity_not_found():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser4',
            'email': 'testuser4@example.com',
            'password': 'testpassword',
            'full_name': 'Test User 4'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser4', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Try to get non-existent activity
    response = client.get(
        '/api/v1/activities/999999',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 404
    assert 'Activity not found' in response.json()['detail']

@pytest.mark.asyncio
async def test_update_activity():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser5',
            'email': 'testuser5@example.com',
            'password': 'testpassword',
            'full_name': 'Test User 5'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser5', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Create an activity
    create_response = client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Cycling',
            'duration_minutes': 30,
            'distance_km': 10.0
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    activity_id = create_response.json()['id']

    # Update the activity
    response = client.put(
        f'/api/v1/activities/{activity_id}',
        json={
            'duration_minutes': 45,
            'notes': 'Extended ride'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json()['duration_minutes'] == 45
    assert response.json()['notes'] == 'Extended ride'

@pytest.mark.asyncio
async def test_delete_activity():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser6',
            'email': 'testuser6@example.com',
            'password': 'testpassword',
            'full_name': 'Test User 6'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser6', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Create an activity
    create_response = client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Walking',
            'duration_minutes': 20
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    activity_id = create_response.json()['id']

    # Delete the activity
    response = client.delete(
        f'/api/v1/activities/{activity_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert 'Activity deleted successfully' in response.json()['message']

    # Verify deletion
    get_response = client.get(
        f'/api/v1/activities/{activity_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_calculate_health_score():
    # First register and login to get token
    register_response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser7',
            'email': 'testuser7@example.com',
            'password': 'testpassword',
            'full_name': 'Test User 7'
        }
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/api/v1/token',
        data={'username': 'testuser7', 'password': 'testpassword'}
    )
    token = login_response.json()['access_token']

    # Create some activities
    client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Running',
            'duration_minutes': 30,
            'calories_burned': 300.0
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    client.post(
        '/api/v1/activities/',
        json={
            'activity_type': 'Cycling',
            'duration_minutes': 45,
            'calories_burned': 400.0
        },
        headers={'Authorization': f'Bearer {token}'}
    )

    # Calculate health score
    response = client.get(
        '/api/v1/activities/calculate-score/?days=7',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), float)
    assert response.json() > 0.0
