from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

TyxterErrorType: TypeAlias = Literal[
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
]


class ErrorFeedbackPointer(TypedDict):
    endpoint: Literal["/v1/feedback"]
    method: Literal["POST"]


class TyxterErrorBody(TypedDict):
    type: TyxterErrorType
    code: str
    message: str
    param: NotRequired[str]
    retry_after_ms: NotRequired[int]
    request_id: NotRequired[str]
    trace_id: NotRequired[str]
    feedback: NotRequired[ErrorFeedbackPointer]


class TyxterErrorResponse(TypedDict):
    error: TyxterErrorBody
