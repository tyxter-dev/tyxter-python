from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import JSONObject

ThroughputTier: TypeAlias = Literal["starter", "growth", "scale"]
SubscriptionBillingRail: TypeAlias = Literal["stripe_card", "pix_annual"]
BillingPackageStatus: TypeAlias = Literal["pending", "succeeded", "failed", "refunded", "expired"]


class CreditBalanceResponse(TypedDict):
    object: Literal["credit_balance"]
    organization_id: str
    balance_brl: str
    currency: Literal["brl"]
    updated_at: str


class PlanOfferingResponse(TypedDict):
    object: Literal["plan_offering"]
    id: str
    display_name: str
    monthly_fee_brl: str
    annual_pix_fee_brl: str
    platform_fee_multiplier: str
    net_transport_rate_brl: str
    throughput_tier: ThroughputTier
    max_phones: int | None


class ListPlansResponse(TypedDict):
    object: Literal["list"]
    data: list[PlanOfferingResponse]


class CurrentPlanResponse(TypedDict):
    object: Literal["subscription"]
    status: Literal["active", "past_due", "canceled", "none"]
    plan_offering_id: str | None
    display_name: str | None
    billing_rail: SubscriptionBillingRail | None
    throughput_tier: ThroughputTier
    max_phones: int | None
    platform_fee_multiplier: str
    net_transport_rate_brl: str
    monthly_fee_brl: str | None
    current_period_end: str | None
    cancel_at_period_end: bool


class SubscribePlanRequest(TypedDict):
    plan_offering_id: str
    rail: NotRequired[SubscriptionBillingRail]


class ChangePlanRequest(TypedDict):
    plan_offering_id: str


class SubscribePixCheckout(TypedDict):
    charge_id: str
    amount_brl: str
    copy_paste: str | None
    qr_code_base64: str | None
    expires_at: str | None


class SubscribePlanResponse(TypedDict):
    object: Literal["subscription_checkout"]
    subscription: CurrentPlanResponse
    pix: SubscribePixCheckout | None


class PlanPackageOfferingResponse(TypedDict):
    id: str
    object: Literal["plan_package_offering"]
    code: str
    name: str
    throughput_tier: ThroughputTier
    price_brl: str
    quota_messages: int
    active: bool
    created_at: str
    updated_at: str


class BillingPackageResponse(TypedDict):
    id: str
    object: Literal["billing_package"]
    status: BillingPackageStatus
    package_code: str
    throughput_tier: ThroughputTier
    amount_brl: str
    quota_messages: int
    quota_remaining: int
    payment_method: Literal["pix", "card"]
    stripe_payment_intent_id: str | None
    created_at: str
    completed_at: str | None


class ListBillingPackagesResponse(TypedDict):
    object: Literal["list"]
    data: list[BillingPackageResponse]
    has_more: bool
    next_cursor: str | None
    available_packages: list[PlanPackageOfferingResponse]


class PurchaseBillingPackageRequest(TypedDict):
    package_code: str
    payment_method: Literal["pix", "card"]


class TopupResponse(TypedDict):
    id: str
    object: Literal["credit_topup"]
    kind: Literal["cash", "package", "x402"]
    status: BillingPackageStatus
    amount_brl: str
    payment_method: Literal["pix", "card", "x402"]
    package_code: str | None
    quota_messages: int | None
    quota_remaining: int | None
    stripe_payment_intent_id: str | None
    stripe_client_secret: str | None
    provider: NotRequired[Literal["stripe", "abacate_pay"]]
    abacate_charge_id: NotRequired[str | None]
    pix_copy_paste: NotRequired[str | None]
    pix_qr_code_base64: NotRequired[str | None]
    pix_expires_at: NotRequired[str | None]
    created_at: str
    completed_at: str | None


class BillingPaymentMethodSetupIntentResponse(TypedDict):
    object: Literal["billing_payment_method_setup_intent"]
    stripe_customer_id: str
    stripe_setup_intent_id: str
    stripe_client_secret: str | None


class BillingPaymentMethodResponse(TypedDict):
    id: str
    object: Literal["billing_payment_method"]
    type: Literal["card"]
    brand: str | None
    last4: str | None
    exp_month: int | None
    exp_year: int | None
    is_default: bool
    status: Literal["active", "deleted"]
    created_at: str
    updated_at: str


class ListBillingPaymentMethodsResponse(TypedDict):
    object: Literal["list"]
    data: list[BillingPaymentMethodResponse]
    has_more: bool
    next_cursor: str | None


SaveBillingPaymentMethodRequest: TypeAlias = JSONObject


class AutoTopupConfigResponse(TypedDict):
    object: Literal["auto_topup_config"]
    enabled: bool
    threshold_brl: str
    amount_brl: str
    payment_method_id: str | None
    last_triggered_at: str | None
    updated_at: str | None


UpdateAutoTopupConfigRequest: TypeAlias = JSONObject


class ListLedgerEntriesResponse(TypedDict):
    object: Literal["list"]
    data: list[JSONObject]
    has_more: bool
    next_cursor: str | None


class InvoiceResponse(TypedDict):
    id: str
    object: Literal["invoice"]
    organization_id: str
    project_id: str
    period_start: str
    period_end: str
    currency: Literal["brl"]
    total_brl: str
    status: Literal["generating", "ready", "failed"]
    error_message: str | None
    created_at: str
    updated_at: str


class ListInvoicesResponse(TypedDict):
    object: Literal["list"]
    data: list[InvoiceResponse]
    has_more: bool
    next_cursor: str | None


class InvoiceDownloadResponse(TypedDict):
    object: Literal["invoice_download"]
    invoice_id: str
    url: str
    expires_at: str


class RateCardEntryResponse(TypedDict):
    id: str
    meter_id: str
    kind: Literal["billed", "meta_reference"]
    conversation_category: Literal["service", "utility", "marketing", "authentication"] | None
    unit_amount: str
    tier_up_to: int | None


class RateCardResponse(TypedDict):
    id: str
    object: Literal["rate_card"]
    name: str
    currency: Literal["brl"]
    effective_from: str
    effective_to: str | None
    entries: list[RateCardEntryResponse]


class ListRateCardsResponse(TypedDict):
    object: Literal["list"]
    data: list[RateCardResponse]
    has_more: bool
    next_cursor: str | None
