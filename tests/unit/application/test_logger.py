from app.infrastructure.logging.logger import configure_logger
import structlog
import json


def test_structlog_json_format(monkeypatch):
    logger = configure_logger("INFO")
    event = logger.info("hello", foo="bar", request_id="req-123")
    # structlog returns None, but logs to stdout; so we test processor
    processor = structlog.get_config()["processors"][-1]
    log_dict = {"event": "hello", "foo": "bar", "request_id": "req-123"}
    rendered = processor(None, None, log_dict)
    assert isinstance(rendered, str)
    data = json.loads(rendered)
    assert data["event"] == "hello"
    assert data["foo"] == "bar"
    assert data["request_id"] == "req-123"
