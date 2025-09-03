import os
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool, StaticPool
from contextlib import contextmanager
from pydantic import PostgresDsn, AnyUrl
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # Database connection settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "health_score_db")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "public")
    
    # Connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # SQLAlchemy settings
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "False").lower() == "true"
    SQL_ECHO_POOL: bool = os.getenv("SQL_ECHO_POOL", "False").lower() == "true"
    
    # Testing settings
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct the database URL from environment variables."""
        if self.TESTING:
            return "sqlite+aiosqlite:///:memory:"
        
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Construct the synchronous database URL for migrations and sync operations."""
        if self.TESTING:
            return "sqlite:///:memory:"
        
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Initialize settings
db_settings = DatabaseSettings()

# Configure SQLAlchemy engine
engine_config = {
    "echo": db_settings.SQL_ECHO,
    "echo_pool": db_settings.SQL_ECHO_POOL,
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_recycle": db_settings.DB_POOL_RECYCLE,
}

# Create database engines
if db_settings.TESTING:
    # Use SQLite in-memory database for testing
    engine_config.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
    
    async_engine = create_async_engine(
        db_settings.DATABASE_URL,
        **engine_config
    )
    
    sync_engine = create_engine(
        db_settings.SYNC_DATABASE_URL,
        **engine_config
    )
else:
    # Use PostgreSQL for production/development
    engine_config.update({
        "pool_size": db_settings.DB_POOL_SIZE,
        "max_overflow": db_settings.DB_MAX_OVERFLOW,
        "pool_timeout": db_settings.DB_POOL_TIMEOUT,
    })
    
    async_engine = create_async_engine(
        db_settings.DATABASE_URL,
        **engine_config
    )
    
    sync_engine = create_engine(
        db_settings.SYNC_DATABASE_URL,
        **engine_config
    )

# Configure session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False,
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
    bind=async_engine,

Base = declarative_base()

@contextmanager
def get_db() -> Generator[SessionLocal, None, None]:
    """Synchronous database session context manager for use with sync code.
    
    Yields:
        Database session
        
    Example:
        with get_db() as db:
            db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session context manager for use with async code.
    
    Yields:
        Async database session
        
    Example:
        async with get_async_db() as db:
            result = await db.execute(select(User))
            user = result.scalars().first()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


# Dependency for FastAPI async endpoints
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI async endpoints.
    
    Returns:
        Async database session
        
    Example in FastAPI route:
        @app.get("/users/{user_id}")
        async def read_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            return user
    """
    async with get_async_db() as session:
        yield session


# For use in synchronous contexts where async is not available
@contextmanager
def get_sync_db() -> Generator[SessionLocal, None, None]:
    """Synchronous database session context manager.
    
    Returns:
        Synchronous database session
        
    Example:
        with get_sync_db() as db:
            user = db.query(User).first()
    """
    with get_db() as db:
        yield db


# Add event listeners for connection handling
@event.listens_for(sync_engine, "engine_connect")
def receive_connection_events(connection, branch):
    """Handle database connection events."""
    if branch:
        # "branch" refers to a sub-connection of a connection
        return
    
    # Set the schema for the connection
    if not db_settings.TESTING and db_settings.DB_SCHEMA != "public":
        connection.execute(f'SET search_path TO {db_settings.DB_SCHEMA},public')
    
    # Log connection events if enabled
    if db_settings.SQL_ECHO:
        print(f"New database connection established: {connection.connection.connection}")


# Add similar event listener for async engine
@event.listens_for(async_engine.sync_engine, "engine_connect")
def receive_async_connection_events(connection, branch):
    """Handle async database connection events."""
    if branch:
        return
    
    if not db_settings.TESTING and db_settings.DB_SCHEMA != "public":
        connection.execute(f'SET search_path TO {db_settings.DB_SCHEMA},public')
    
    if db_settings.SQL_ECHO:
        print(f"New async database connection established: {connection.connection.connection}")
