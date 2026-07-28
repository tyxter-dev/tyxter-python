from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast

from .types import ErrorFeedbackPointer, TyxterErrorType

_SUPPORTED_ERROR_TYPES = {
    "authentication_error",
    "authorization_error",
    "payment_required",
    "validation_error",
    "idempotency_conflict",
    "rate_limited",
    "not_found",
    "conflict",
    "provider_error",
    "internal_error",
    "service_unavailable",
}


class TyxterError(Exception):
    """Base exception for all Tyxter SDK errors."""


class TyxterAPIError(TyxterError):
    """Error returned by the Tyxter API."""

    def __init__(
        self,
        *,
        status_code: int,
        type: TyxterErrorType | Literal["api_error"],
        code: str,
        message: str,
        param: str | None = None,
        request_id: str | None = None,
        trace_id: str | None = None,
        retry_after_ms: int | None = None,
        feedback: ErrorFeedbackPointer | None = None,
        body: object = None,
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
        self.feedback = feedback
        self.body = body


class TyxterConnectionError(TyxterError):
    """Network-level failure before the Tyxter API returned a response."""


class TyxterMediaUploadError(TyxterError):
    """A capability-URL media upload returned a non-success response."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"Media upload failed with HTTP {status_code}.")
        self.status_code = status_code


def parse_api_error(status_code: int, body: object) -> TyxterAPIError:
    if isinstance(body, Mapping) and isinstance(body.get("error"), Mapping):
        error = cast(Mapping[object, object], body["error"])
        message = _string_value(error.get("message")) or f"Tyxter API request failed: {status_code}"
        return TyxterAPIError(
            status_code=status_code,
            type=_error_type(error.get("type")),
            code=_string_value(error.get("code")) or f"http_{status_code}",
            message=message,
            param=_string_value(error.get("param")),
            request_id=_string_value(error.get("request_id")),
            trace_id=_string_value(error.get("trace_id")),
            retry_after_ms=_int_value(error.get("retry_after_ms")),
            feedback=_feedback_value(error.get("feedback")),
            body=body,
        )

    return TyxterAPIError(
        status_code=status_code,
        type="api_error",
        code=f"http_{status_code}",
        message=f"Tyxter API request failed: {status_code}",
        body=body,
    )


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _int_value(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _error_type(value: object) -> TyxterErrorType | Literal["api_error"]:
    if isinstance(value, str) and value in _SUPPORTED_ERROR_TYPES:
        return cast(TyxterErrorType, value)
    return "api_error"


def _feedback_value(value: object) -> ErrorFeedbackPointer | None:
    if not isinstance(value, Mapping):
        return None
    if value.get("endpoint") != "/v1/feedback" or value.get("method") != "POST":
        return None
    return {"endpoint": "/v1/feedback", "method": "POST"}
