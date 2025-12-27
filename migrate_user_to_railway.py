#!/usr/bin/env python3
"""
Script to migrate user credentials from localhost database to Railway database.
This exports the user's password hash from localhost and inserts it into Railway.
"""

import asyncio
import asyncpg
import sys
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


async def get_localhost_user(email: str):
    """Get user from localhost database."""
    local_db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'tradingbot'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    
    print(f"Connecting to localhost database: {local_db_config['database']}...")
    conn = await asyncpg.connect(**local_db_config)
    
    try:
        user = await conn.fetchrow(
            "SELECT id, email, password_hash, full_name, is_active, created_at FROM users WHERE email = $1",
            email
        )
        return user
    finally:
        await conn.close()


async def insert_user_to_railway(email: str, password_hash: str, full_name: str = None, railway_db_url: str = None):
    """Insert user into Railway database."""
    if not railway_db_url:
        railway_db_url = input("Enter Railway DATABASE_URL: ").strip()
    
    if not railway_db_url:
        print("Error: DATABASE_URL is required")
        sys.exit(1)
    
    # Parse DATABASE_URL
    parsed = urlparse(railway_db_url)
    
    db_config = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password
    }
    
    print(f"Connecting to Railway database: {db_config['database']}...")
    conn = await asyncpg.connect(**db_config)
    
    try:
        # Check if user already exists
        existing = await conn.fetchrow(
            "SELECT id, email FROM users WHERE email = $1",
            email
        )
        
        if existing:
            print(f"User {email} already exists in Railway database. Updating password hash...")
            await conn.execute(
                "UPDATE users SET password_hash = $1, full_name = $2 WHERE email = $3",
                password_hash,
                full_name,
                email
            )
            print(f"✅ Updated user {email} in Railway database")
        else:
            # Insert new user
            await conn.execute(
                "INSERT INTO users (email, password_hash, full_name, is_active) VALUES ($1, $2, $3, $4)",
                email,
                password_hash,
                full_name,
                True
            )
            print(f"✅ Inserted user {email} into Railway database")
            
    finally:
        await conn.close()


async def main():
    print("=" * 60)
    print("User Migration: Localhost → Railway")
    print("=" * 60)
    print()
    
    # Get email from user
    email = input("Enter your email address: ").strip()
    if not email:
        print("Error: Email is required")
        sys.exit(1)
    
    # Get user from localhost
    print(f"\n1. Fetching user '{email}' from localhost database...")
    user = await get_localhost_user(email)
    
    if not user:
        print(f"❌ User '{email}' not found in localhost database")
        print("\nTip: You can also manually sign up on Railway using the same email/password")
        sys.exit(1)
    
    print(f"✅ Found user: {user['email']}")
    print(f"   Full Name: {user.get('full_name', 'N/A')}")
    print(f"   Active: {user.get('is_active', True)}")
    
    # Confirm migration
    print(f"\n2. Migrating user to Railway...")
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Migration cancelled")
        sys.exit(0)
    
    # Insert into Railway
    await insert_user_to_railway(
        email=user['email'],
        password_hash=user['password_hash'],
        full_name=user.get('full_name')
    )
    
    print("\n" + "=" * 60)
    print("✅ Migration complete!")
    print("=" * 60)
    print(f"\nYou can now log in to Railway with:")
    print(f"  Email: {email}")
    print(f"  Password: (your original password)")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

