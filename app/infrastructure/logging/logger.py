import structlog
import logging
import sys
import os


class RequestIdProcessor:
    def __call__(self, logger, method_name, event_dict):
        request_id = event_dict.get("request_id") or os.getenv("REQUEST_ID")
        if request_id:
            event_dict["request_id"] = request_id
        return event_dict


def configure_logger(log_level: str = "INFO"):
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            RequestIdProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level.upper()),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()
