from dataclasses import dataclass
from typing import Any


class Status:
    """Value object para status de Item."""

    VALID = {"pending", "initialized", "processed", "failed"}

    def __init__(self, value: str):
        if value not in self.VALID:
            raise ValueError(f"Invalid status: {value}")
        self.value = value

    def __str__(self):
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Status) and self.value == other.value


@dataclass(frozen=True)
class Item:
    """Entidade de domínio: Item."""

    id: str
    name: str
    status: Status

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValueError("id must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.status, Status):
            raise ValueError("status must be a Status instance")
