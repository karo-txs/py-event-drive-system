from app.infrastructure.external.http_client import HttpExternalApiClient
from app.infrastructure.persistence.repository import ItemRepository
from app.infrastructure.logging.logger import configure_logger
from app.infrastructure.messaging.factory import get_message_bus
from app.infrastructure.persistence.db import get_session_local
from app.config.settings import Settings

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)


async def provide_session(settings: Settings):
    SessionLocal = get_session_local(settings.DB_URL)
    return SessionLocal()


def provide_repository(settings: Settings):
    SessionLocal = get_session_local(settings.DB_URL)
    session = SessionLocal()
    return ItemRepository(session)


def provide_message_bus(settings: Settings):
    return get_message_bus(settings)


def provide_external_api(settings: Settings):
    return HttpExternalApiClient(base_url=settings.EXTERNAL_API_BASE_URL)
