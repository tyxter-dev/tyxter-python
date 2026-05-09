from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

if TYPE_CHECKING:
    from tyxter.client import Tyxter

JSONDict = dict[str, Any]


class Resource:
    def __init__(self, client: Tyxter) -> None:
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: JSONDict | None = None,
        params: JSONDict | None = None,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> Any:
        return self._client._request(
            method,
            path,
            json=json,
            params=_clean_params(params),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )


def path_id(name: str, value: str) -> str:
    if not value:
        raise ValueError(f"{name} is required")
    return quote(value, safe="")


def _clean_params(params: JSONDict | None) -> JSONDict | None:
    if params is None:
        return None
    clean = {key: value for key, value in params.items() if value is not None}
    return clean or None
