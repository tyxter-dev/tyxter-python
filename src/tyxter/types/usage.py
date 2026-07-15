from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import TypedDict

from .common import Environment

UsageGroupBy: TypeAlias = Literal[
    "destination_country",
    "template_id",
    "meta_pass_through_fee",
    "tyxter_markup",
    "package_consumption",
]
ConversationCategory: TypeAlias = Literal["service", "utility", "marketing", "authentication"]


class UsageSummaryBucket(TypedDict):
    meter_id: str
    environment: Environment
    group_key: str | None
    quantity: int
    cost_brl: str
    meta_pass_through_fee_brl: str
    tyxter_markup_brl: str
    package_messages_debited: int


class UsageSummaryResponse(TypedDict):
    object: Literal["usage_summary"]
    currency: Literal["brl"]
    period_start: str
    period_end: str
    group_by: UsageGroupBy | None
    buckets: list[UsageSummaryBucket]
    total_cost_brl: str


class UsageRecordTransport(TypedDict):
    list_rate_brl: str
    net_rate_brl: str
    plan_multiplier: str
    list_amount_brl: str
    discount_amount_brl: str
    net_amount_brl: str
    plan_offering_id: str | None
    meta_reference_meter_key: str | None
    meta_reference_rate_brl: str | None


class UsageRecordResponse(TypedDict):
    id: str
    object: Literal["usage_record"]
    meter_id: str
    conversation_category: ConversationCategory | None
    environment: Environment
    quantity: int
    cost_brl: str
    uncollected_brl: str
    currency: Literal["brl"]
    transport: UsageRecordTransport | None
    message_id: str | None
    package_topup_id: str | None
    package_messages_debited: int
    trace_id: str
    recorded_at: str


class ListUsageRecordsResponse(TypedDict):
    object: Literal["list"]
    data: list[UsageRecordResponse]
    has_more: bool
    next_cursor: str | None
