#!/usr/bin/env python3
"""
Initialize an admin user in the database.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import async_session
from app.db.models.user import User, UserRole

async def create_admin_user():
    """Create an admin user if one doesn't exist."""
    print("Checking for admin user...")
    
    admin_email = "admin@healthscore.com"
    admin_password = "admin"  # In production, use a secure password from environment variables
    
    async with async_session() as session:
        # Check if admin already exists
        existing_admin = await session.execute(
            User.select().where(User.email == admin_email)
        )
        if existing_admin.scalar_one_or_none() is not None:
            print("Admin user already exists.")
            return
        
        # Create admin user
        hashed_password = get_password_hash(admin_password)
        admin = User(
            email=admin_email,
            hashed_password=hashed_password,
            first_name="Admin",
            last_name="User",
            is_superuser=True,
            role=UserRole.ADMIN,
            is_active=True,
            email_verified=True
        )
        
        session.add(admin)
        await session.commit()
        print(f"Admin user created with email: {admin_email}")
        print("Please change the password after first login!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
