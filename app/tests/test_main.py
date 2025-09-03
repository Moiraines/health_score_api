import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to the Health Score API'}

@pytest.mark.asyncio
async def test_docs_endpoint(client):
    response = await client.get('/docs')
    assert response.status_code == 200
    assert 'Swagger UI' in response.text

@pytest.mark.asyncio
async def test_openapi_endpoint(client):
    response = await client.get('/openapi.json')
    assert response.status_code == 200
    assert 'openapi' in response.json()
    assert response.json()['info']['title'] == 'Health Score API'
