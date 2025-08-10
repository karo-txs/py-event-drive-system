from app.application.ports import ExternalApiClient
import httpx
import os


class HttpExternalApiClient(ExternalApiClient):
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv(
            "EXTERNAL_API_BASE_URL", "https://httpbin.org"
        )
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def get(self, path: str, params: dict | None = None):
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, data: dict):
        resp = await self._client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()

    async def get_json(self, path: str):
        resp = await self._client.get(path)
        resp.raise_for_status()
        return resp.json()

    async def post_json(self, path: str, payload: dict):
        resp = await self._client.post(path, json=payload)
        resp.raise_for_status()
        return resp.json()
