import pytest
from datetime import datetime, timedelta
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health_score import HealthScoreCreate
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.core.security import create_access_token

# Test data
TEST_USER = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password': 'testpassword',
    'full_name': 'Test User'
}

TEST_HEALTH_SCORE = {
    'score': 75.5,
    'notes': 'Feeling good today'
}

def get_auth_headers(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}

@pytest.mark.asyncio
async def test_create_health_score(client, db: AsyncSession):
    # Create test user
    user_service = UserService(db)
    test_user = UserCreate(**TEST_USER)
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Create health score
    response = client.post(
        '/api/v1/health-scores/',
        json=TEST_HEALTH_SCORE,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data['score'] == TEST_HEALTH_SCORE['score']
    assert data['notes'] == TEST_HEALTH_SCORE['notes']
    assert 'id' in data
    assert 'user_id' in data
    assert data['user_id'] == db_user.id

@pytest.mark.asyncio
async def test_create_health_score_unauthorized(client):
    response = client.post(
        '/api/v1/health-scores/',
        json={
            'score': 80.0,
            'notes': 'Unauthorized attempt'
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'Not authenticated' in response.json()['detail']

@pytest.mark.asyncio
async def test_get_health_scores(client, db: AsyncSession):
    # Create test user and health scores
    user_service = UserService(db)
    test_user = UserCreate(
        username='testuser2',
        email='testuser2@example.com',
        password='testpassword2',
        full_name='Test User 2'
    )
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Create multiple health scores
    for i in range(3):
        score_data = {
            'score': 70.0 + (i * 5.0),
            'notes': f'Test score {i}'
        }
        response = await client.post(
            '/api/v1/health-scores/',
            json=score_data,
            headers=get_auth_headers(token)
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Get health scores
    response = await client.get(
        '/api/v1/health-scores/',
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all('id' in item and 'score' in item for item in data)
    assert all('user_id' in score for score in data)

@pytest.mark.asyncio
async def test_get_health_scores_by_date_range(client, db: AsyncSession):
    # Create test user and health scores
    user_service = UserService(db)
    test_user = UserCreate(
        username='testuser3',
        email='testuser3@example.com',
        password='testpassword3',
        full_name='Test User 3'
    )
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Create health scores with different dates
    today = datetime.utcnow().date()
    for i in range(3):
        score_date = today - timedelta(days=i)
        score_data = {
            'score': 70.0 + (i * 5.0),
            'notes': f'Test score {i}',
            'timestamp': score_date.isoformat()
        }
        response = await client.post(
            '/api/v1/health-scores/',
            json=score_data,
            headers=get_auth_headers(token)
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Get health scores for today
    start_date = today.isoformat()
    end_date = today.isoformat()
    
    response = await client.get(
        f'/api/v1/health-scores/?start_date={start_date}&end_date={end_date}',
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['timestamp'].startswith(today.isoformat())
    assert all(score['notes'] in ['Today', 'Yesterday'] for score in data)

@pytest.mark.asyncio
async def test_get_health_scores_unauthorized(client):
    response = await client.get('/api/v1/health-scores/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'Not authenticated' in response.json()['detail']

@pytest.mark.asyncio
async def test_get_health_score(client, db: AsyncSession):
    # Create test user and health score
    user_service = UserService(db)
    test_user = UserCreate(
        username='testuser4',
        email='testuser4@example.com',
        password='testpassword4',
        full_name='Test User 4'
    )
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Create health score
    create_response = await client.post(
        '/api/v1/health-scores/',
        json=TEST_HEALTH_SCORE,
        headers=get_auth_headers(token)
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    health_score_id = create_response.json()['id']
    
    # Get the health score
    response = await client.get(
        f'/api/v1/health-scores/{health_score_id}',
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == health_score_id
    assert data['score'] == TEST_HEALTH_SCORE['score']
    assert data['notes'] == TEST_HEALTH_SCORE['notes']
    assert data['user_id'] == db_user.id

@pytest.mark.asyncio
async def test_get_health_score_not_found(client, db: AsyncSession):
    # Create test user
    user_service = UserService(db)
    test_user = UserCreate(
        username='testuser5',
        email='testuser5@example.com',
        password='testpassword5',
        full_name='Test User 5'
    )
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Try to get non-existent health score
    response = await client.get(
        '/api/v1/health-scores/999999',
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Health score not found' in response.json()['detail']

@pytest.mark.asyncio
async def test_update_health_score(client, db: AsyncSession):
    # Create test user and health score
    user_service = UserService(db)
    test_user = UserCreate(
        username='testuser6',
        email='testuser6@example.com',
        password='testpassword6',
        full_name='Test User 6'
    )
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Create health score
    create_response = await client.post(
        '/api/v1/health-scores/',
        json=TEST_HEALTH_SCORE,
        headers=get_auth_headers(token)
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    health_score_id = create_response.json()['id']
    
    # Update health score
    update_data = {
        'score': 85.0,
        'notes': 'Updated notes'
    }
    
    response = await client.put(
        f'/api/v1/health-scores/{health_score_id}',
        json=update_data,
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == health_score_id
    assert data['score'] == update_data['score']
    assert data['notes'] == update_data['notes']
    assert data['user_id'] == db_user.id

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_delete_health_score(client, db: AsyncSession):
    # Create test user and health score
    user_service = UserService(db)
    test_user = UserCreate(
        username='testuser7',
        email='testuser7@example.com',
        password='testpassword7',
        full_name='Test User 7'
    )
    db_user = await user_service.create_user(test_user)
    
    # Create token
    token = create_access_token(data={"sub": db_user.username})
    
    # Create health score
    create_response = client.post(
        '/api/v1/health-scores/',
        json=TEST_HEALTH_SCORE,
        headers=get_auth_headers(token)
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    health_score_id = create_response.json()['id']
    
    # Delete health score
    response = client.delete(
        f'/api/v1/health-scores/{health_score_id}',
        headers=get_auth_headers(token)
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(
        f'/api/v1/health-scores/{health_score_id}',
        headers=get_auth_headers(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_health_scores_unauthorized(client):
    response = await client.get('/api/v1/health-scores/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'Not authenticated' in response.json()['detail']

@pytest.mark.asyncio
async def test_get_health_score(client):
    # First register and login to get token
    register_response = await client.post(
        '/api/v1/auth/register',
        json={
            'username': 'testuser3',
            'email': 'testuser3@example.com',
            'password': 'testpassword3',
            'full_name': 'Test User 3'
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = await client.post(
        '/api/v1/auth/token',
        data={'username': 'testuser3', 'password': 'testpassword3'}
    )
    token = login_response.json()['access_token']

    # Create a health score
    create_response = await client.post(
        '/api/v1/health-scores/',
        json={
            'score': 85.0,
            'notes': 'Excellent day'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    health_score_id = create_response.json()['id']

    # Get the health score by ID
    response = await client.get(
        f'/api/v1/health-scores/{health_score_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == health_score_id
    assert data['score'] == 85.0
    assert data['notes'] == 'Excellent day'

@pytest.mark.asyncio
async def test_get_health_score_not_found(client):
    # First register and login to get token
    register_response = await client.post(
        '/api/v1/auth/register',
        json={
            'username': 'testuser4',
            'email': 'testuser4@example.com',
            'password': 'testpassword4',
            'full_name': 'Test User 4'
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = await client.post(
        '/api/v1/auth/token',
        data={'username': 'testuser4', 'password': 'testpassword4'}
    )
    token = login_response.json()['access_token']

    # Try to get non-existent health score
    response = await client.get(
        '/api/v1/health-scores/99999',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Health score not found' in response.json()['detail']

@pytest.mark.asyncio
async def test_update_health_score(client):
    # First register and login to get token
    register_response = await client.post(
        '/api/v1/auth/register',
        json={
            'username': 'testuser5',
            'email': 'testuser5@example.com',
            'password': 'testpassword5',
            'full_name': 'Test User 5'
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = await client.post(
        '/api/v1/auth/token',
        data={'username': 'testuser5', 'password': 'testpassword5'}
    )
    token = login_response.json()['access_token']

    # Create a health score
    create_response = await client.post(
        '/api/v1/health-scores/',
        json={
            'score': 70.0,
            'notes': 'Initial score'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    health_score_id = create_response.json()['id']

    # Update the health score
    update_response = await client.put(
        f'/api/v1/health-scores/{health_score_id}',
        json={
            'score': 75.0,
            'notes': 'Updated score'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data['score'] == 75.0
    assert data['notes'] == 'Updated score'
    assert 'updated_at' in data

@pytest.mark.asyncio
async def test_delete_health_score(client):
    # First register and login to get token
    register_response = await client.post(
        '/api/v1/auth/register',
        json={
            'username': 'testuser6',
            'email': 'testuser6@example.com',
            'password': 'testpassword6',
            'full_name': 'Test User 6'
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = await client.post(
        '/api/v1/auth/token',
        data={'username': 'testuser6', 'password': 'testpassword6'}
    )
    token = login_response.json()['access_token']

    # Create a health score
    create_response = await client.post(
        '/api/v1/health-scores/',
        json={
            'score': 90.0,
            'notes': 'To be deleted'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    health_score_id = create_response.json()['id']

    # Delete the health score
    delete_response = await client.delete(
        f'/api/v1/health-scores/{health_score_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json() == {"message": "Health score deleted successfully"}

    # Verify it's deleted
    response = await client.get(
        f'/api/v1/health-scores/{health_score_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
