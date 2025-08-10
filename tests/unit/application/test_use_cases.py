from app.application.use_cases.process_event import ProcessEvent
from app.application.dtos import ProcessEventInput
from app.domain.entities import Status
import pytest


class FakeRepo:
    def __init__(self):
        self.saved = []

    async def get(self, id):
        for i in self.saved:
            if i.id == id:
                return i
        return None

    async def save(self, obj):
        self.saved.append(obj)


class FakeBus:
    def __init__(self):
        self.events = []

    async def send(self, event):
        self.events.append(event)

    async def receive(self):
        return {}

    async def ack(self, message_id):
        pass

    async def nack(self, message_id):
        pass


class FakeApi:
    async def get(self, path, params=None):
        return {"ok": True}

    async def post(self, path, data):
        return {"ok": True}


@pytest.mark.asyncio
async def test_process_event_success():
    repo = FakeRepo()
    bus = FakeBus()
    api = FakeApi()
    use_case = ProcessEvent(repo, bus, api)
    dto = ProcessEventInput(payload={"id": "123", "name": "TestItem"})
    out = await use_case.execute(dto)
    assert out.success is True
    assert out.item_id == "123"
    assert any(e["type"] == "ItemToProcess" for e in bus.events)
    assert any(i.status == Status("initialized") for i in repo.saved)
