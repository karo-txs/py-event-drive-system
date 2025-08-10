from app.application.dtos import ProcessEventOutput
from app.application.ports import Repository
from app.domain.entities import Status
from dataclasses import replace


class ProcessItemFromQueue:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def execute(self, item_id: str) -> ProcessEventOutput:
        item = await self.repo.get(item_id)
        if not item:
            raise ValueError("Item não encontrado")
        item_processed = replace(item, status=Status("processed"))
        await self.repo.save(item_processed)
        return ProcessEventOutput(
            success=True,
            message="Item processed",
            item_id=item.id
        )
