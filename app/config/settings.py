from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    DB_URL: str = "sqlite+aiosqlite:///:memory:"
    MESSAGE_BROKER: Literal["sqs", "rabbitmq", "in_memory"] = "in_memory"
    SQS_QUEUE_URL: str = ""
    RABBITMQ_URL: str = ""
    EXTERNAL_API_BASE_URL: str = "https://httpbin.org"
    OTEL_ENABLED: bool = False

    model_config = ConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), case_sensitive=False
    )

    @field_validator("MESSAGE_BROKER")
    @classmethod
    def validate_broker(cls, v):
        if v not in ("sqs", "rabbitmq", "in_memory"):
            raise ValueError("MESSAGE_BROKER must be one of: sqs, rabbitmq, in_memory")
        return v
