from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

WebhookEndpointStatus: TypeAlias = Literal["active", "disabled"]
WebhookEndpointDisabledDetailFailureClass: TypeAlias = Literal[
    "auth_rejected", "server_error", "unreachable", "timeout"
]


class WebhookEndpointDisabledDetail(TypedDict):
    last_status_code: int | None
    failure_class: WebhookEndpointDisabledDetailFailureClass


class CreateWebhookEndpointRequest(TypedDict):
    url: str
    subscribed_events: list[str]
    description: NotRequired[str]


class UpdateWebhookEndpointRequest(TypedDict, total=False):
    url: str
    subscribed_events: list[str]
    description: str | None
    status: WebhookEndpointStatus


class WebhookEndpointResponse(TypedDict):
    id: str
    object: Literal["webhook_endpoint"]
    url: str
    description: str | None
    subscribed_events: list[str]
    status: WebhookEndpointStatus
    disabled_reason: str | None
    disabled_detail: WebhookEndpointDisabledDetail | None
    last_failure_at: str | None
    last_success_at: str | None
    environment: Environment
    created_at: str
    updated_at: str


class CreateWebhookEndpointResponse(WebhookEndpointResponse):
    signing_secret: str


class RotateWebhookSigningSecretResponse(WebhookEndpointResponse):
    signing_secret: str


class ListWebhookEndpointsResponse(TypedDict):
    object: Literal["list"]
    data: list[WebhookEndpointResponse]
    has_more: bool
    next_cursor: str | None


class TestWebhookEndpointResponse(TypedDict):
    object: Literal["webhook_test"]
    webhook_event_id: str
    webhook_endpoint_id: str
    status: Literal["pending"]


class DeleteWebhookEndpointResponse(TypedDict):
    id: str
    deleted: bool


MessageMediaTranscriptionWebhookEventType: TypeAlias = Literal[
    "message.media_transcribed", "message.media_transcription_failed"
]


class MessageWebhookIdentity(TypedDict):
    type: str
    id: str


class MessageWebhookData(TypedDict):
    message_id: str
    status: str
    channel: Literal["whatsapp", "instagram"]
    sender: MessageWebhookIdentity
    recipient: MessageWebhookIdentity
    provider_message_id: str | None
    metadata: object | None


class MessageMediaTranscribedWebhookTranscript(TypedDict):
    id: str
    media_asset_id: str
    status: Literal["succeeded"]
    provider: str
    model: str
    language: str | None
    text: str | None
    duration_seconds: int
    completed_at: str


class MessageMediaTranscribedWebhookData(MessageWebhookData):
    transcript: MessageMediaTranscribedWebhookTranscript


class _WebhookEventEnvelope(TypedDict):
    id: str
    created_at: str
    occurred_at: NotRequired[str]
    environment: Environment
    trace_id: str


class MessageMediaTranscribedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["message.media_transcribed"]
    data: MessageMediaTranscribedWebhookData


class MessageMediaTranscriptionFailedWebhookTranscript(TypedDict):
    id: str
    media_asset_id: str
    status: Literal["failed"]
    error_code: str
    error_message: str | None
    language: str | None
    completed_at: str


class MessageMediaTranscriptionFailedWebhookData(MessageWebhookData):
    transcript: MessageMediaTranscriptionFailedWebhookTranscript


class MessageMediaTranscriptionFailedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["message.media_transcription_failed"]
    data: MessageMediaTranscriptionFailedWebhookData


MessageMediaTranscriptionWebhookTranscript: TypeAlias = (
    MessageMediaTranscribedWebhookTranscript | MessageMediaTranscriptionFailedWebhookTranscript
)
MessageMediaTranscriptionWebhookData: TypeAlias = (
    MessageMediaTranscribedWebhookData | MessageMediaTranscriptionFailedWebhookData
)
MessageMediaTranscriptionWebhookEnvelope: TypeAlias = (
    MessageMediaTranscribedWebhookEnvelope | MessageMediaTranscriptionFailedWebhookEnvelope
)
