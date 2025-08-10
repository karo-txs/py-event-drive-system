from app.infrastructure.messaging.in_memory_bus import InMemoryMessageBus
from app.infrastructure.messaging.rabbitmq_bus import RabbitMQMessageBus
from app.infrastructure.messaging.sqs_bus import SqsMessageBus


def get_message_bus(settings) -> object:
    broker = getattr(settings, "MESSAGE_BROKER", "in_memory")
    if broker == "sqs":
        return SqsMessageBus(settings.SQS_QUEUE_URL)
    elif broker == "rabbitmq":
        return RabbitMQMessageBus(settings.RABBITMQ_URL)
    else:
        return InMemoryMessageBus()
