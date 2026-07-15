from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, Required, TypedDict

from .common import JSONObject
from .messages import MediaMessagePayload, MessageChannel

InboundSandboxMessageRequest = TypedDict(
    "InboundSandboxMessageRequest",
    {
        "from": Required[str],
        "to": Required[str],
        "type": Required[Literal["text", "media", "interactive", "flow"]],
        "channel": NotRequired[MessageChannel],
        "text": NotRequired[dict[Literal["body"], str]],
        "media": NotRequired[MediaMessagePayload],
        "interactive": NotRequired[JSONObject],
        "flow": NotRequired[JSONObject],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)


class SandboxTemplateStatusRequest(TypedDict):
    status: Literal["rejected", "paused", "disabled"]
    rejection_reason: NotRequired[str]


class SandboxEnvironment(TypedDict):
    id: str
    kind: Literal["sandbox"]
    project_id: str


class SandboxAPIKey(TypedDict):
    id: str
    key_prefix: str | None
    scopes: list[str]
    can_create_api_keys: Literal[False]
    api_key_creation: Literal["dashboard_or_api_keys_endpoint"]


class SandboxSender(TypedDict):
    default_sender_id: str | None
    phone_number: str | None
    display_name: str | None
    status: str | None
    outbound_messages_require_sender: Literal[True]
    inbound_simulation_requires_sender: Literal[False]


class SandboxSigningHeaders(TypedDict):
    id: Literal["tyxter-webhook-id"]
    timestamp: Literal["tyxter-webhook-timestamp"]
    signature: Literal["tyxter-webhook-signature"]


class SandboxWebhooks(TypedDict):
    active_endpoint_count: int
    listen_endpoint: Literal["/v1/webhook-events/listen"]
    retrieve_listen_event_endpoint: Literal["/v1/webhook-events/listen/:outbox_event_id"]
    inbound_event_type: Literal["message.received"]
    supported_listen_event_types: list[str]
    signing_headers: SandboxSigningHeaders


class SandboxCapabilities(TypedDict):
    simulate_inbound: bool
    listen_for_webhooks: bool
    send_outbound_messages: bool


class SandboxQuickstartResponse(TypedDict):
    object: Literal["sandbox_quickstart"]
    environment: SandboxEnvironment
    api_key: SandboxAPIKey
    sender: SandboxSender
    webhooks: SandboxWebhooks
    capabilities: SandboxCapabilities
    missing_scopes: list[str]
