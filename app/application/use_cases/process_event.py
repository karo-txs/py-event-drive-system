from app.application.dtos import ProcessEventInput, ProcessEventOutput
from app.application.ports import Repository, MessageBus, ExternalApiClient
from app.infrastructure.logging.logger import configure_logger
from app.application.errors import ApplicationError
from app.domain.entities import Item, Status
from app.config.settings import Settings
import uuid

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)


class ProcessEvent:
    """Caso de uso: processar evento recebido."""

    def __init__(self, repo: Repository[Item], bus: MessageBus, api: ExternalApiClient):
        self.repo = repo
        self.bus = bus
        self.api = api

    async def execute(self, dto: ProcessEventInput) -> ProcessEventOutput:
        try:
            payload = dto.payload
            item_id = payload.get("id") or str(uuid.uuid4())
            name = payload.get("name", "unknown")

            item = Item(id=item_id, name=name, status=Status("pending"))
            await self.repo.save(item)

            logger.info("Chama API externa", item_id=item.id)
            await self.api.post(
                "/post", {"item_id": item.id, "status": str(item.status)}
            )

            logger.info("Atualiza status", item_id=item.id)
            processed_item = Item(
                id=item.id, name=item.name, status=Status("initialized")
            )
            await self.repo.save(processed_item)

            logger.info("Publica evento", item_id=item.id)
            await self.bus.send({"type": "ItemToProcess", "item_id": item.id})

            return ProcessEventOutput(
                success=True, message="initialized", item_id=item.id
            )
        except Exception as e:
            logger.error("Erro ao processar evento", error=str(e))
            raise ApplicationError(f"Erro ao processar evento: {e}")
