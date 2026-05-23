import asyncio
from app.db import AsyncSessionLocal
from app.models import AIGeneration, AIGenerationStatus
from sqlalchemy import update

async def run():
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(AIGeneration)
            .where(AIGeneration.status.in_([AIGenerationStatus.PENDING, AIGenerationStatus.PROCESSING]))
            .values(status=AIGenerationStatus.FAILED, error_details={"message": "Forcefully failed due to previous bug"})
        )
        await session.commit()
        print("Updated stuck records to FAILED.")

if __name__ == "__main__":
    asyncio.run(run())
