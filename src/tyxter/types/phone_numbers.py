from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

PhoneNumberSource: TypeAlias = Literal["salvy", "byon"]
PhoneNumberStatus: TypeAlias = Literal[
    "requested",
    "provisioning",
    "provisioned",
    "verifying",
    "active",
    "failed",
    "release_requested",
    "released",
    "disconnected",
]
PhoneQualityRating: TypeAlias = Literal["green", "yellow", "red", "unknown"]
PhoneMessagingTier: TypeAlias = Literal[
    "tier_50", "tier_250", "tier_1k", "tier_10k", "tier_100k", "unlimited", "unknown"
]
MetaThroughputTier: TypeAlias = Literal["1", "2", "3", "4", "unlimited"]


class ProvisionPhoneNumberRequest(TypedDict):
    ddd: str
    display_name: NotRequired[str]


class ConnectPhoneNumberRequest(TypedDict):
    phone: str
    meta_phone_number_id: str
    display_name: NotRequired[str]


class TransferPhoneNumberRequest(TypedDict):
    source_project_id: str
    source_environment_id: str
    target_project_id: str
    target_environment_id: str
    confirm_phone_number_id: str
    reason: NotRequired[str]


PhoneNumberRecentMessageResponse = TypedDict(
    "PhoneNumberRecentMessageResponse",
    {
        "id": str,
        "object": Literal["message"],
        "direction": str,
        "type": str,
        "status": str,
        "from": str | None,
        "to": str | None,
        "template_name": str | None,
        "created_at": str,
    },
)


class PhoneNumberResponse(TypedDict):
    id: str
    object: Literal["phone_number"]
    source: PhoneNumberSource
    status: PhoneNumberStatus
    environment: Environment
    display_name: str | None
    ddd: str | None
    phone: str | None
    provider_number_id: str | None
    meta_phone_number_id: str | None
    waba_id: str | None
    quality_rating: PhoneQualityRating
    messaging_tier: PhoneMessagingTier
    messaging_limit_tier: str | None
    meta_throughput_tier: MetaThroughputTier | None
    meta_quality_rating: str | None
    # When the Meta-reported health above was last read from Meta. ``None``
    # means it has never been read yet; an older timestamp means those fields
    # are as of that moment, since a failed refresh leaves both the values and
    # this marker untouched.
    meta_health_synced_at: str | None
    current_24h_unique_recipients: int
    verification_code: str | None
    verification_code_received_at: str | None
    monthly_fee_brl: str | None
    error_code: str | None
    error_message: str | None
    created_at: str
    updated_at: str
    activated_at: str | None
    released_at: str | None
    recent_messages: list[PhoneNumberRecentMessageResponse]


class ListPhoneNumbersResponse(TypedDict):
    object: Literal["list"]
    data: list[PhoneNumberResponse]
    has_more: bool
    next_cursor: str | None


class AvailableRegionResponse(TypedDict):
    ddd: str
    country: Literal["BR"]
    monthly_fee_brl: str
    state: str | None
    region_label: str | None


class ListAvailableRegionsResponse(TypedDict):
    object: Literal["list"]
    data: list[AvailableRegionResponse]
