from app.infrastructure.logging.logger import configure_logger
from app.application.ports import MessageBus
from app.config.settings import Settings
import aio_pika
import json

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)


class RabbitMQMessageBus(MessageBus):
    def __init__(self, url: str | None = None, queue_name: str = "events"):
        self.url = url
        self.queue_name = queue_name
        self._conn = None
        self._channel = None
        self._queue = None

    async def _connect(self):
        if not self._conn:
            self._conn = await aio_pika.connect_robust(self.url)
            self._channel = await self._conn.channel()
            self._queue = await self._channel.declare_queue(
                self.queue_name, durable=True
            )

    async def send(self, event: dict) -> None:
        await self._connect()
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(event).encode()),
            routing_key=self.queue_name,
        )

    async def receive(self) -> dict:
        await self._connect()
        queue = await self._channel.declare_queue(self.queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        return {"body": json.loads(message.body.decode())}
                    except json.JSONDecodeError:
                        logger.error("Mensagem inválida na fila", body=message.body)
                        continue

    async def ack(self, message_id: str) -> None:
        # message_id is actually the message object
        if hasattr(message_id, "ack"):
            await message_id.ack()

    async def nack(self, message_id: str) -> None:
        if hasattr(message_id, "nack"):
            await message_id.nack()
