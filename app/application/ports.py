from typing import Protocol, TypeVar, Generic, Any
from abc import abstractmethod

T = TypeVar("T")


class Repository(Protocol, Generic[T]):
    """Porta para persistência genérica."""

    @abstractmethod
    async def get(self, id: str) -> T | None: ...
    @abstractmethod
    async def save(self, obj: T) -> None: ...


class MessageBus(Protocol):
    """Porta para mensageria."""

    @abstractmethod
    async def send(self, event: dict) -> None: ...
    @abstractmethod
    async def receive(self) -> dict: ...
    @abstractmethod
    async def ack(self, message_id: str) -> None: ...
    @abstractmethod
    async def nack(self, message_id: str) -> None: ...


class ExternalApiClient(Protocol):
    """Porta para integração HTTP externa."""

    @abstractmethod
    async def get(self, path: str, params: dict | None = None) -> Any: ...
    @abstractmethod
    async def post(self, path: str, data: dict) -> Any: ...
