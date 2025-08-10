from sqlalchemy.ext.asyncio import AsyncSession
from app.application.ports import Repository
from app.domain.entities import Item
from sqlalchemy import select
from .models import ItemModel
from typing import Optional


class ItemRepository(Repository[Item]):
    """Implementação do Repository para Item usando SQLAlchemy async."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: str) -> Optional[Item]:
        result = await self.session.execute(select(ItemModel).where(ItemModel.id == id))
        row = result.scalar_one_or_none()
        return row.to_entity() if row else None

    async def save(self, obj: Item) -> None:
        model = ItemModel.from_entity(obj)
        await self.session.merge(model)
        await self.session.commit()
