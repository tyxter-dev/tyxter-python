from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

ProviderName: TypeAlias = Literal["meta", "iniciador", "abacate_pay"]
ProviderConnectionStatus: TypeAlias = Literal["pending", "connected", "suspended", "disconnected"]
ProviderTokenSource: TypeAlias = Literal["manual", "embedded_signup"]
ProviderConnectionChannel: TypeAlias = Literal[
    "whatsapp", "instagram", "payments", "agentic_payments"
]
ProviderReadinessStatus: TypeAlias = Literal[
    "missing", "connected", "pending", "suspended", "disconnected", "selection_required"
]
ProviderCredentialSetupTarget: TypeAlias = Literal[
    "meta.whatsapp",
    "abacate_pay.payments",
    "iniciador.payments",
    "iniciador.agentic_payments",
    "openai.tts",
    "elevenlabs.tts",
    "xai.tts",
]
ProviderCredentialSetupSessionStatus: TypeAlias = Literal[
    "pending", "completed", "denied", "expired"
]


class PaymentReceiverProfile(TypedDict, total=False):
    name: str
    tax_id: str
    bank_name: str
    ispb: str
    issuer: str
    account_number: str
    account_type: Literal["CACC", "SLRY", "SVGS", "TRAN"]


class PaymentProviderCapabilities(TypedDict):
    hosted_payment_link: bool
    fixed_receiver: bool
    webhook_hmac: bool
    dynamic_receiver: bool


class AgenticPaymentProviderCapabilities(TypedDict):
    mcp_tools: bool
    reusable_authorizations: bool
    hosted_authorization: bool
    hosted_payment_confirmation: bool
    polling: bool


class RegisterMetaConnectionRequest(TypedDict):
    display_name: str
    access_token: str
    channel: NotRequired[ProviderConnectionChannel]
    waba_id: NotRequired[str]
    phone_number_id: NotRequired[str]
    ig_business_account_id: NotRequired[str]
    page_id: NotRequired[str]
    token_source: NotRequired[ProviderTokenSource]
    token_expires_at: NotRequired[str | None]


class ExchangeMetaOAuthCodeRequest(TypedDict):
    code: str
    waba_id: str
    phone_number_id: str
    display_name: NotRequired[str]
    business_id: NotRequired[str]


class RotateProviderConnectionTokenRequest(TypedDict):
    access_token: str
    token_source: NotRequired[ProviderTokenSource]
    token_expires_at: NotRequired[str | None]


class ProviderConnectionResponse(TypedDict):
    id: str
    object: Literal["provider_connection"]
    provider: ProviderName
    channel: ProviderConnectionChannel
    status: ProviderConnectionStatus
    display_name: str
    environment: Environment
    waba_id: str | None
    phone_number_id: str | None
    ig_business_account_id: str | None
    page_id: str | None
    provider_account_id: str | None
    payment_receiver: PaymentReceiverProfile | None
    payment_capabilities: PaymentProviderCapabilities | None
    agentic_capabilities: AgenticPaymentProviderCapabilities | None
    default_participant_id: str | None
    agent_id: str | None
    agentic_api_base_url: str | None
    webhook_secret_configured: bool
    credential_last_four: NotRequired[str | None]
    token_source: ProviderTokenSource | None
    token_expires_at: str | None
    token_refreshed_at: str | None
    token_rotated_at: str | None
    created_at: str
    updated_at: str
    disconnected_at: str | None


class DeleteProviderConnectionResponse(TypedDict):
    id: str
    object: Literal["provider_connection"]
    status: Literal["disconnected"]


class ListProviderConnectionsResponse(TypedDict):
    object: Literal["list"]
    data: list[ProviderConnectionResponse]
    has_more: bool
    next_cursor: str | None


class MessagingChannelReadiness(TypedDict):
    ready: bool
    status: ProviderReadinessStatus
    connection_id: str | None
    reason: str | None


class PaymentsChannelReadiness(TypedDict):
    ready: bool
    status: ProviderReadinessStatus
    active_connection_id: str | None
    active_mode: Literal["sandbox_default", "iniciador", "abacate_pay"] | None
    reason: str | None


class ProviderConnectionChannels(TypedDict):
    whatsapp: MessagingChannelReadiness
    instagram: MessagingChannelReadiness
    payments: PaymentsChannelReadiness
    agentic_payments: MessagingChannelReadiness


class ProviderConnectionStatusResponse(TypedDict):
    object: Literal["provider_connection_status"]
    environment: Environment
    channels: ProviderConnectionChannels


class MetaOnboardingExtras(TypedDict):
    version: Literal["v3"]
    sessionInfoVersion: Literal["3"]


class MetaOnboardingLoginOptions(TypedDict):
    config_id: str
    response_type: Literal["code"]
    override_default_response_type: Literal[True]
    extras: MetaOnboardingExtras


class MetaOnboardingConfigResponse(TypedDict):
    object: Literal["meta_onboarding_config"]
    mode: Literal["embedded_signup"]
    app_id: str
    config_id: str
    graph_api_version: str
    sdk_url: str
    allowed_message_origins: list[str]
    message_type: Literal["WA_EMBEDDED_SIGNUP"]
    login_options: MetaOnboardingLoginOptions
    completion_endpoint: Literal["/v1/provider-connections/meta/oauth"]
    manual_credentials_endpoint: Literal["/v1/provider-connections/meta"]


class CreateProviderCredentialSetupSessionRequest(TypedDict):
    target: ProviderCredentialSetupTarget


class ProviderCredentialSetupSessionResponse(TypedDict):
    object: Literal["provider_credential_setup_session"]
    request_id: str
    target: ProviderCredentialSetupTarget
    status: ProviderCredentialSetupSessionStatus
    project_id: str
    project_slug: str
    environment_id: str
    environment: Environment
    setup_url: str
    poll_url: str
    expires_at: str
    completed_at: str | None
    denied_at: str | None
    completed_provider_connection_id: str | None
    completed_tts_provider: Literal["openai", "elevenlabs", "xai"] | None
    created_at: str
    updated_at: str
