from app.config.settings import Settings
from pydantic import ValidationError
import pytest


def test_valid_broker():
    s = Settings(DB_URL="sqlite:///:memory:", MESSAGE_BROKER="sqs")
    assert s.MESSAGE_BROKER == "sqs"
    s2 = Settings(DB_URL="sqlite:///:memory:", MESSAGE_BROKER="rabbitmq")
    assert s2.MESSAGE_BROKER == "rabbitmq"
    s3 = Settings(DB_URL="sqlite:///:memory:", MESSAGE_BROKER="in_memory")
    assert s3.MESSAGE_BROKER == "in_memory"


def test_invalid_broker():
    with pytest.raises(ValidationError):
        Settings(DB_URL="sqlite:///:memory:", MESSAGE_BROKER="foo")
