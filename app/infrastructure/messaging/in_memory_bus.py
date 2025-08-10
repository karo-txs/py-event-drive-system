from app.application.ports import MessageBus
import asyncio


class InMemoryMessageBus(MessageBus):
    def __init__(self):
        self._queue = asyncio.Queue()

    async def send(self, event: dict) -> None:
        await self._queue.put(event)

    async def receive(self) -> dict:
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=1)
        except asyncio.TimeoutError:
            return {}

    async def ack(self, message_id: str) -> None:
        pass  # No-op

    async def nack(self, message_id: str) -> None:
        pass  # No-op
