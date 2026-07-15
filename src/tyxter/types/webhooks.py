from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

WebhookEndpointStatus: TypeAlias = Literal["active", "disabled"]


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


class DeleteWebhookEndpointResponse(TypedDict):
    id: str
    deleted: bool
