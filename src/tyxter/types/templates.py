from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment, JSONObject

TemplateCategory: TypeAlias = Literal["marketing", "utility", "authentication"]
TemplateStatus: TypeAlias = Literal[
    "draft", "submitted", "approved", "rejected", "paused", "disabled", "orphaned"
]
TemplateQuality: TypeAlias = Literal["green", "yellow", "red", "unknown"]


class TemplateAuthoringSignal(TypedDict):
    code: str
    severity: Literal["info", "warning", "critical"]
    source: Literal["authoring", "provider", "usage"]
    message: str
    field: str | None


class TemplateResponse(TypedDict):
    id: str
    object: Literal["template"]
    name: str
    language: str
    category: TemplateCategory
    status: TemplateStatus
    environment: Environment
    components: list[JSONObject]
    provider_template_id: str | None
    rejection_reason: str | None
    provider_quality: TemplateQuality
    authoring_signals: list[TemplateAuthoringSignal]
    submitted_at: str | None
    approved_at: str | None
    created_at: str
    updated_at: str


class CreateTemplateRequest(TypedDict):
    name: str
    language: str
    category: TemplateCategory
    components: list[JSONObject]


class TemplateGenerationRequest(TypedDict):
    description: str
    language: str
    category: TemplateCategory
    name: NotRequired[str]
    template_type: NotRequired[Literal["text", "media"]]


class UpdateTemplateRequest(TypedDict, total=False):
    name: str
    language: str
    category: TemplateCategory
    components: list[JSONObject]


class DuplicateTemplateRequest(TypedDict, total=False):
    name: str
    language: str
    category: TemplateCategory


class ListTemplatesResponse(TypedDict):
    object: Literal["list"]
    data: list[TemplateResponse]
    has_more: bool
    next_cursor: str | None


class TemplateGenerationResponse(TypedDict):
    object: Literal["template_generation"]
    name: str
    language: str
    category: TemplateCategory
    components: list[JSONObject]
    authoring_signals: list[TemplateAuthoringSignal]


class TemplateApprovalAnalytics(TypedDict):
    submissions: int
    approved: int
    rejected: int
    pending: int
    approval_rate: float


class TemplateSendAnalytics(TypedDict):
    total: int
    accepted: int
    queued: int
    sending: int
    sent: int
    provider_accepted: int
    delivered: int
    read: int
    failed: int
    cancelled: int
    expired: int
    success_rate: float
    last_sent_at: str | None


class TemplateAnalyticsResponse(TypedDict):
    object: Literal["template_analytics"]
    template_id: str
    approvals: TemplateApprovalAnalytics
    sends: TemplateSendAnalytics


class EstimateTemplateCostRequest(TypedDict, total=False):
    recipients: int


class TemplateCostEstimateResponse(TypedDict):
    object: Literal["template_cost_estimate"]
    template_id: str
    category: TemplateCategory
    meter_id: str
    recipients: int
    unit_amount_brl: str
    total_brl: str
    currency: Literal["brl"]
    rate_card_id: str
