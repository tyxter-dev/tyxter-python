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


PublicFeedbackReportStatus: TypeAlias = Literal["open", "resolved", "dismissed"]
PublicFeedbackReportResolutionDisposition: TypeAlias = Literal["resolved", "dismissed"]


class PublicFeedbackReportClosedResolution(TypedDict):
    disposition: PublicFeedbackReportResolutionDisposition
    public_summary: str
    published_at: str


class PublicFeedbackReportReopenedResolution(TypedDict):
    disposition: Literal["reopened"]
    public_summary: str | None
    published_at: str


PublicFeedbackReportResolution: TypeAlias = (
    PublicFeedbackReportClosedResolution | PublicFeedbackReportReopenedResolution
)


class PublicFeedbackReportResponse(TypedDict):
    id: str
    object: Literal["feedback_report"]
    status: PublicFeedbackReportStatus
    message_excerpt: str
    created_at: str
    latest_resolution: PublicFeedbackReportResolution | None


class ListPublicFeedbackReportsResponse(TypedDict):
    object: Literal["list"]
    data: list[PublicFeedbackReportResponse]
    has_more: bool
    next_cursor: str | None
