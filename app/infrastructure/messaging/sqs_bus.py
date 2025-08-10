from app.application.ports import MessageBus
import aioboto3
import os


class SqsMessageBus(MessageBus):
    def __init__(self, queue_url: str | None = None):
        self.queue_url = queue_url or os.getenv("SQS_QUEUE_URL")

    async def send(self, event: dict) -> None:
        session = aioboto3.Session()
        async with session.client("sqs") as client:
            await client.send_message(QueueUrl=self.queue_url, MessageBody=str(event))

    async def receive(self) -> dict:
        session = aioboto3.Session()
        async with session.client("sqs") as client:
            response = await client.receive_message(
                QueueUrl=self.queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1
            )
            return response.get("Messages", [{}])[0]

    async def ack(self, message_id: str) -> None:
        session = aioboto3.Session()
        async with session.client("sqs") as client:
            await client.delete_message(
                QueueUrl=self.queue_url, ReceiptHandle=message_id
            )

    async def nack(self, message_id: str) -> None:
        # SQS: nack = do nothing (message will be retried)
        pass
