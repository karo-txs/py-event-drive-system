from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from app.domain.entities import Item, Status
from sqlalchemy import String

Base = declarative_base()


class ItemModel(Base):
    __tablename__ = "items"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    def to_entity(self) -> Item:
        return Item(id=self.id, name=self.name, status=Status(self.status))

    @staticmethod
    def from_entity(item: Item) -> "ItemModel":
        return ItemModel(id=item.id, name=item.name, status=str(item.status))
