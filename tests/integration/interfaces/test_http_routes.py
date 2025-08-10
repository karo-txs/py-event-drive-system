from fastapi.testclient import TestClient
from app.interfaces.http.main import create_app
import pytest


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_process_mock(monkeypatch, client):
    # Mock ProcessEvent para não executar lógica real
    async def dummy_execute(self, dto):
        return {
            "success": True,
            "item_id": "abc",
            "message": "ok",
            "status": None,
        }

    monkeypatch.setattr(
        "app.application.use_cases.process_event.ProcessEvent.execute", dummy_execute
    )
    resp = client.post("/process", json={"id": "abc", "name": "Test"})
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["item_id"] == "abc"
