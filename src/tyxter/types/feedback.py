from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

FeedbackContext: TypeAlias = dict[str, str]


class FeedbackRelatedError(TypedDict, total=False):
    code: str
    request_id: str
    trace_id: str


class CreateFeedbackRequest(TypedDict):
    message: str
    related_error: NotRequired[FeedbackRelatedError]
    context: NotRequired[FeedbackContext]


class FeedbackReceiptResponse(TypedDict):
    id: str
    object: Literal["feedback_receipt"]
    received_at: str
    redacted: bool
