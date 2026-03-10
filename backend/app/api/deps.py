import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

_is_lambda = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

_engine_kwargs: dict = dict(
    pool_pre_ping=True,
    pool_size=1 if _is_lambda else 5,
    max_overflow=2 if _is_lambda else 10,
)
if _is_lambda:
    _engine_kwargs["pool_recycle"] = 300

async_engine = create_async_engine(
    settings.database_url,
    **_engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
