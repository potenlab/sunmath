"""Seed script for initial admin settings."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.api.deps import AsyncSessionLocal
from app.models.history import AdminSettings

INITIAL_SETTINGS = [
    {
        "key": "similarity_threshold",
        "value": "0.85",
        "description": "Minimum similarity score to flag problems as duplicates",
    },
    {
        "key": "confidence_threshold",
        "value": "0.90",
        "description": "Minimum confidence for LLM grading to be accepted without review",
    },
    {
        "key": "duplicate_detection_mode",
        "value": "warn",
        "description": "How to handle duplicate problems: warn, block, or ignore",
    },
]


async def seed():
    async with AsyncSessionLocal() as session:
        for item in INITIAL_SETTINGS:
            result = await session.execute(
                select(AdminSettings).where(AdminSettings.key == item["key"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  Skipping '{item['key']}' (already exists)")
            else:
                session.add(AdminSettings(**item))
                print(f"  Inserted '{item['key']}'")
        await session.commit()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
