"""
scripts/init_db.py
------------------
Initialize the database for deployment:
1. Run Alembic migrations (schema creation)
2. Seed default users and institution

Run: python -m scripts.init_db
"""

from __future__ import annotations

import asyncio
import sys
import subprocess

from sqlalchemy import select

from app.core.security import hash_password
from app.config import settings
from app.db import AsyncSessionLocal, engine
from app.models import Base, Institution, User, UserRole


INSTITUTION_NAME = "EduFlow HQ"

DEFAULT_USERS = [
    {
        "email": "admin@eduflow.edu",
        "password": "admin123",
        "name": "EduFlow Admin",
        "role": UserRole.ADMIN,
        "phone": "+91 90000 00001",
    },
    {
        "email": "institution.admin@eduflow.edu",
        "password": "institution123",
        "name": "Institution Admin",
        "role": UserRole.INSTITUTION_ADMIN,
        "phone": "+91 90000 00002",
    },
    {
        "email": "educator@eduflow.edu",
        "password": "educator123",
        "name": "Demo Educator",
        "role": UserRole.EDUCATOR,
        "phone": "+91 90000 00003",
    },
    {
        "email": "student@eduflow.edu",
        "password": "student123",
        "name": "Demo Student",
        "role": UserRole.STUDENT,
        "phone": "+91 90000 00004",
    },
]


async def seed_database() -> None:
    """Seed the database with default institution and users."""
    print("[init_db] Starting database seeding...")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing_inst = (
            await db.execute(select(Institution).where(Institution.name == INSTITUTION_NAME))
        ).scalars().first()

        if existing_inst:
            institution = existing_inst
            print(f"[init_db] Institution already exists: {institution.name!r}")
        else:
            institution = Institution(name=INSTITUTION_NAME, address="Online")
            db.add(institution)
            await db.flush()
            print(f"[init_db] Created institution: {institution.name!r}  id={institution.id}")

        institution_admin_id: str | None = institution.admin_id

        for entry in DEFAULT_USERS:
            existing_user = (
                await db.execute(select(User).where(User.email == entry["email"]))
            ).scalars().first()

            if existing_user:
                existing_user.name = entry["name"]
                existing_user.phone = entry["phone"]
                existing_user.role = entry["role"]
                existing_user.institution_id = institution.id
                print(f"[init_db] User already exists (updated): {existing_user.email!r}")
                current_user = existing_user
            else:
                current_user = User(
                    name=entry["name"],
                    email=entry["email"],
                    password=hash_password(entry["password"]),
                    role=entry["role"],
                    institution_id=institution.id,
                    phone=entry["phone"],
                )
                db.add(current_user)
                await db.flush()
                print(f"[init_db] Created user: {current_user.email!r}  id={current_user.id}")

            if entry["role"] == UserRole.INSTITUTION_ADMIN:
                institution_admin_id = current_user.id

        institution.admin_id = institution_admin_id

        await db.commit()
        print("[init_db] Database seeding completed successfully!")


def run_migrations() -> None:
    """Run Alembic migrations."""
    print("[init_db] Running Alembic migrations...")
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=False,
        )
        print("[init_db] Migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"[init_db] Migrations failed: {e}")
        raise


async def main() -> None:
    """Main initialization flow."""
    print("[init_db] ========================================")
    print("[init_db] Starting EduFlow Database Initialization")
    print(f"[init_db] Database: {settings.DATABASE_URL}")
    print("[init_db] ========================================")

    try:
        # Run migrations first
        run_migrations()

        # Then seed the database
        await seed_database()

        print("[init_db] ========================================")
        print("[init_db] Database initialization completed!")
        print("[init_db] Admin credentials:")
        print("[init_db]   Email: admin@eduflow.edu")
        print("[init_db]   Password: admin123")
        print("[init_db] ========================================")

    except Exception as e:
        print(f"[init_db] ERROR: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
