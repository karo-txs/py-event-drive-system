from app.infrastructure.messaging.rabbitmq_bus import RabbitMQMessageBus
from unittest.mock import AsyncMock, patch
import pytest


@pytest.mark.asyncio
async def test_rabbitmq_bus_send_receive_mock():
    with (
        patch.object(RabbitMQMessageBus, "send", new_callable=AsyncMock) as mock_send,
        patch.object(
            RabbitMQMessageBus, "receive", new_callable=AsyncMock
        ) as mock_receive,
    ):
        bus = RabbitMQMessageBus(url="amqp://fake/", queue_name="test_events")
        event = {"hello": "world"}
        await bus.send(event)
        mock_send.assert_awaited_once_with(event)

        # Simula retorno do receive
        mock_receive.return_value = {"body": {"hello": "world"}}
        received = await bus.receive()
        assert "body" in received
        assert "hello" in received["body"]
