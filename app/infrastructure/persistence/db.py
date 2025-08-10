from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from typing import AsyncGenerator, Optional
from sqlalchemy.orm import sessionmaker
from typing import Optional
from .models import Base
import os


async def init_db(db_url: Optional[str] = None):
    engine = get_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_engine(db_url: Optional[str] = None) -> AsyncEngine:
    url = db_url or os.getenv(
        "DB_URL", "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
    )
    return create_async_engine(url, echo=True, future=True)


def get_session_local(db_url: Optional[str] = None):
    engine = get_engine(db_url)
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def get_session(
    db_url: Optional[str] = None,
) -> AsyncGenerator[AsyncSession, None]:
    SessionLocal = get_session_local(db_url)
    async with SessionLocal() as session:
        yield session
