"""
scripts/seed.py
---------------
Seeds a baseline institution and default users for the admin, institution admin,
educator, and student portals.

Run:  python -m scripts.seed
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
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


async def seed() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing_inst = (
            await db.execute(select(Institution).where(Institution.name == INSTITUTION_NAME))
        ).scalars().first()

        if existing_inst:
            institution = existing_inst
            print(f"[seed] Institution already exists: {institution.name!r}")
        else:
            institution = Institution(name=INSTITUTION_NAME, address="Online")
            db.add(institution)
            await db.flush()
            print(f"[seed] Created institution: {institution.name!r}  id={institution.id}")

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
                print(f"[seed] User already exists: {existing_user.email!r}")
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
                print(f"[seed] Created user: {current_user.email!r}  id={current_user.id}")

            if entry["role"] == UserRole.INSTITUTION_ADMIN:
                institution_admin_id = current_user.id

        institution.admin_id = institution_admin_id

        await db.commit()
        print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(seed())
