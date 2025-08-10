from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ProcessEventInput:
    payload: Dict[str, Any]


@dataclass
class ProcessEventOutput:
    success: bool
    message: str
    item_id: str | None = None
