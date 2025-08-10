from app.infrastructure.external.http_client import HttpExternalApiClient
import pytest


@pytest.mark.asyncio
async def test_get_json_httpbin():
    client = HttpExternalApiClient(base_url="https://httpbin.org")
    data = await client.get_json("/json")
    assert "slideshow" in data
