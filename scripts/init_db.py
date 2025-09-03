#!/usr/bin/env python3
"""
Initialize the database and run migrations.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.base import Base
from app.db.session import async_engine, async_session

async def init_models():
    """Create database tables."""
    print("Creating database tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

async def drop_models():
    """Drop all database tables. (Use with caution!)"""
    if input("Are you sure you want to drop all tables? (y/n): ").lower() == 'y':
        print("Dropping all database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("All database tables dropped!")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--drop", 
        action="store_true", 
        help="Drop all tables before creating them"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        asyncio.run(drop_models())
    
    asyncio.run(init_models())
