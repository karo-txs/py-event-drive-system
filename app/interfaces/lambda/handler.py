from app.infrastructure.providers import (
    provide_repository,
    provide_message_bus,
    provide_external_api,
)
from app.application.use_cases.process_event import ProcessEvent
from app.infrastructure.logging.logger import configure_logger
from app.application.dtos import ProcessEventInput
from app.config.settings import Settings
import asyncio
import json

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)


def handler(event, context):
    try:
        # SQS event
        if "Records" in event:
            for record in event["Records"]:
                payload = json.loads(record["body"])
                asyncio.run(_process(payload))
            return {"statusCode": 200, "body": "Processed SQS batch"}
        # API Gateway event
        elif "body" in event:
            payload = json.loads(event["body"])
            result = asyncio.run(_process(payload))
            return {"statusCode": 200, "body": json.dumps(result)}
        else:
            logger.error("Evento desconhecido", event=event)
            return {"statusCode": 400, "body": "Bad event"}
    except Exception as e:
        logger.error("Erro no handler", error=str(e))
        return {"statusCode": 500, "body": str(e)}


async def _process(payload):
    repo = provide_repository(settings)
    bus = provide_message_bus(settings)
    api = provide_external_api(settings)
    use_case = ProcessEvent(repo, bus, api)
    dto = ProcessEventInput(payload=payload)
    result = await use_case.execute(dto)
    logger.info("Processado com sucesso", item_id=result.item_id)
    return {"success": result.success, "item_id": result.item_id}
