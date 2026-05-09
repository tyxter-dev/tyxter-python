from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class TyxterError(Exception):
    """Base exception for all Tyxter SDK errors."""


class TyxterAPIError(TyxterError):
    """Error returned by the Tyxter API."""

    def __init__(
        self,
        *,
        status_code: int,
        type: str,
        code: str,
        message: str,
        param: str | None = None,
        request_id: str | None = None,
        trace_id: str | None = None,
        retry_after_ms: int | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.type = type
        self.code = code
        self.message = message
        self.param = param
        self.request_id = request_id
        self.trace_id = trace_id
        self.retry_after_ms = retry_after_ms
        self.body = body


class TyxterConnectionError(TyxterError):
    """Network-level failure before the Tyxter API returned a response."""


def parse_api_error(status_code: int, body: Any) -> TyxterAPIError:
    if isinstance(body, Mapping) and isinstance(body.get("error"), Mapping):
        error = body["error"]
        message = _string_value(error.get("message")) or f"Tyxter API request failed: {status_code}"
        return TyxterAPIError(
            status_code=status_code,
            type=_string_value(error.get("type")) or "api_error",
            code=_string_value(error.get("code")) or f"http_{status_code}",
            message=message,
            param=_string_value(error.get("param")),
            request_id=_string_value(error.get("request_id")),
            trace_id=_string_value(error.get("trace_id")),
            retry_after_ms=_int_value(error.get("retry_after_ms")),
            body=body,
        )

    return TyxterAPIError(
        status_code=status_code,
        type="api_error",
        code=f"http_{status_code}",
        message=f"Tyxter API request failed: {status_code}",
        body=body,
    )


def _string_value(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _int_value(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    return None
