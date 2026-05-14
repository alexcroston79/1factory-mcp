import asyncio
from typing import Any

import httpx

from onefactory_mcp.config import get_base_url, get_headers


PAGE_SIZE = 500
MAX_RESULTS = 5000
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0
SUCCESS_CODES = (200, 201, 202, 204)


class OneFactoryClient:
    """Async HTTP client for the 1Factory API with auto-pagination and rate-limit backoff."""

    def __init__(self) -> None:
        self.base_url = get_base_url()
        self.headers = get_headers()
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "OneFactoryClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(MAX_RETRIES):
            resp = await self._client.request(method, path, **kwargs)
            if resp.status_code != 429:
                return resp
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            reset = (
                resp.headers.get("x-ratelimit-minute-reset")
                or resp.headers.get("x-ratelimit-day-reset")
            )
            if reset:
                try:
                    delay = max(delay, int(reset))
                except ValueError:
                    pass
            await asyncio.sleep(delay)
        return resp

    @staticmethod
    def _format_error(resp: httpx.Response) -> str:
        if resp.status_code == 401:
            return (
                "API error 401: authentication failed — check ONEFACTORY_KEY and "
                "ONEFACTORY_ORG environment variables"
            )
        try:
            err = resp.json()
        except Exception:
            err = {"code": resp.status_code, "message": resp.text}
        return f"API error {resp.status_code}: {err}"

    @staticmethod
    def _parse_body(resp: httpx.Response) -> Any:
        if resp.status_code == 204 or not resp.content:
            return {}
        try:
            return resp.json()
        except Exception:
            return {}

    async def paginate(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Auto-paginate a list endpoint, returning all results up to MAX_RESULTS."""
        all_results: list[dict[str, Any]] = []
        page = 0
        base_params = dict(params) if params else {}

        while len(all_results) < MAX_RESULTS:
            p = {**base_params, "page": page, "page_size": PAGE_SIZE}
            resp = await self._request("GET", path, params=p)

            if resp.status_code >= 400:
                return all_results

            data = self._parse_body(resp)
            if not isinstance(data, list) or not data:
                break

            all_results.extend(data)
            if len(data) < PAGE_SIZE:
                break
            page += 1

        return all_results

    async def get(self, path: str, params: dict[str, Any] | None = None) -> tuple[Any, str | None]:
        """GET a resource. Returns (data, error_message)."""
        resp = await self._request("GET", path, params=params)
        if resp.status_code >= 400:
            return None, self._format_error(resp)
        return self._parse_body(resp), None

    async def put(self, path: str, json_body: Any) -> tuple[Any, str | None]:
        resp = await self._request("PUT", path, json=json_body)
        if resp.status_code >= 400:
            return None, self._format_error(resp)
        return self._parse_body(resp), None

    async def post(self, path: str, json_body: Any) -> tuple[Any, str | None]:
        resp = await self._request("POST", path, json=json_body)
        if resp.status_code >= 400:
            return None, self._format_error(resp)
        return self._parse_body(resp), None
