from __future__ import annotations

from typing import Any

import httpx

from ._version import __version__
from .errors import TyxterConnectionError, parse_api_error


class Tyxter:
    """Synchronous Tyxter API client.

    Resource surfaces are added incrementally in R5a. The core request layer is
    intentionally private so resources can keep a small public API.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.tyxter.com",
        timeout: float = 30.0,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
        )
        self._owns_client = http_client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Tyxter:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: MappingJSON | None = None,
        params: MappingJSON | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        headers = self._headers(idempotency_key=idempotency_key, has_body=json is not None)
        try:
            response = self._client.request(
                method,
                path,
                headers=headers,
                json=json,
                params=params,
            )
        except httpx.RequestError as exc:
            raise TyxterConnectionError(str(exc)) from exc

        body = self._parse_response(response)
        if response.is_error:
            raise parse_api_error(response.status_code, body)
        return body

    def _headers(self, *, idempotency_key: str | None, has_body: bool) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"tyxter-python/{__version__}",
        }
        if has_body:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _parse_response(self, response: httpx.Response) -> Any:
        if response.status_code == 204 or not response.content:
            return None

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return response.text

        try:
            return response.json()
        except ValueError:
            return response.text


MappingJSON = dict[str, Any]
