from app.application.use_cases.process_item_from_queue import ProcessItemFromQueue
from app.infrastructure.providers import provide_repository, provide_message_bus
from app.infrastructure.logging.logger import configure_logger
from app.config.settings import Settings
import asyncio

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)


async def worker_loop():
    settings = Settings()
    repo = provide_repository(settings)
    bus = provide_message_bus(settings)
    use_case = ProcessItemFromQueue(repo)
    logger.info("Worker iniciado, aguardando mensagens...")
    while True:
        msg = await bus.receive()
        item_id = msg.get("body", {}).get("item_id") or msg.get("item_id")
        if item_id:
            logger.info("Processando item da fila...", item_id=item_id)
            result = await use_case.execute(item_id)
            logger.info("Item processado", item=result)
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(worker_loop())
