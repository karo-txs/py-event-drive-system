from app.infrastructure.persistence.db import get_engine, get_session_local, init_db
from app.infrastructure.persistence.repository import ItemRepository
from app.domain.entities import Item, Status
import tempfile
import pytest
import os


@pytest.mark.asyncio
async def test_item_repository_crud():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    SQLITE_URL = f"sqlite+aiosqlite:///{db_path}"
    try:
        engine = get_engine(SQLITE_URL)
        await init_db(SQLITE_URL)
        SessionLocal = get_session_local(SQLITE_URL)
        async with SessionLocal() as session:
            repo = ItemRepository(session)
            item = Item(id="i1", name="Test", status=Status("pending"))
            await repo.save(item)
            loaded = await repo.get("i1")
            assert loaded is not None
            assert loaded.id == "i1"
            updated = Item(id="i1", name="Test", status=Status("processed"))
            await repo.save(updated)
            loaded2 = await repo.get("i1")
            assert loaded2.status == Status("processed")
        await engine.dispose()
    finally:
        pass
