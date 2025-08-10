from app.infrastructure.messaging.in_memory_bus import InMemoryMessageBus
import pytest


@pytest.mark.asyncio
async def test_in_memory_bus_send_receive():
    bus = InMemoryMessageBus()
    event = {"foo": "bar"}
    await bus.send(event)
    received = await bus.receive()
    assert received == event


@pytest.mark.asyncio
async def test_in_memory_bus_empty():
    bus = InMemoryMessageBus()
    result = await bus.receive()
    assert result == {}
