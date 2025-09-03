import os
import sys
import asyncio
from typing import AsyncGenerator, Generator

# Set TESTING environment variable before importing the app
os.environ['TESTING'] = '1'

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.config import settings

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db, get_async_db

# Create a test database with in-memory SQLite
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override the database URL for testing
settings.DATABASE_URL = TEST_SQLALCHEMY_DATABASE_URL

# Create async engine for testing
async_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False}
)

# Create async session factory
TestingSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

# Dependency override for async database session
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Create tables before tests
@pytest_asyncio.fixture(autouse=True)
async def create_test_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db():
    """Create a new database session for a test."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@pytest.fixture
def client():
    """Create a test client that uses the test database."""
    # Override the database dependency
    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_async_db] = override_get_db
    
    # Create a test client with the FastAPI app
    with TestClient(fastapi_app) as test_client:
        yield test_client
    
    # Clean up overrides
    fastapi_app.dependency_overrides.clear()
