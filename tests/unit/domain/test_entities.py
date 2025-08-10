from app.domain.entities import Item, Status
import pytest


def test_status_valid():
    s = Status("pending")
    assert str(s) == "pending"
    assert s == Status("pending")


def test_status_invalid():
    with pytest.raises(ValueError):
        Status("foo")


def test_item_valid():
    item = Item(id="1", name="Test", status=Status("pending"))
    assert item.id == "1"
    assert item.name == "Test"
    assert item.status == Status("pending")


def test_item_invalid():
    with pytest.raises(ValueError):
        Item(id="", name="Test", status=Status("pending"))
    with pytest.raises(ValueError):
        Item(id="1", name="", status=Status("pending"))
    with pytest.raises(ValueError):
        Item(id="1", name="Test", status="pending")
