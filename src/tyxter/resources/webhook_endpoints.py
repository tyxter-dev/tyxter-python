from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreateWebhookEndpointRequest,
    CreateWebhookEndpointResponse,
    ListWebhookEndpointsResponse,
    RotateWebhookSigningSecretResponse,
    UpdateWebhookEndpointRequest,
    WebhookEndpointResponse,
)

from ._base import Resource, path_id


class WebhookEndpointsResource(Resource):
    def create(
        self,
        payload: CreateWebhookEndpointRequest,
        *,
        idempotency_key: str | None = None,
    ) -> CreateWebhookEndpointResponse:
        return cast(
            CreateWebhookEndpointResponse,
            self._request(
                "POST",
                "/v1/webhook-endpoints",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListWebhookEndpointsResponse:
        return cast(
            ListWebhookEndpointsResponse,
            self._request(
                "GET",
                "/v1/webhook-endpoints",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def get(self, webhook_endpoint_id: str) -> WebhookEndpointResponse:
        return cast(
            WebhookEndpointResponse,
            self._request(
                "GET",
                f"/v1/webhook-endpoints/{path_id('webhook_endpoint_id', webhook_endpoint_id)}",
            ),
        )

    def retrieve(self, webhook_endpoint_id: str) -> WebhookEndpointResponse:
        return self.get(webhook_endpoint_id)

    def update(
        self,
        webhook_endpoint_id: str,
        payload: UpdateWebhookEndpointRequest,
        *,
        idempotency_key: str | None = None,
    ) -> WebhookEndpointResponse:
        return cast(
            WebhookEndpointResponse,
            self._request(
                "PATCH",
                f"/v1/webhook-endpoints/{path_id('webhook_endpoint_id', webhook_endpoint_id)}",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def delete(
        self,
        webhook_endpoint_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> WebhookEndpointResponse:
        return cast(
            WebhookEndpointResponse,
            self._request(
                "DELETE",
                f"/v1/webhook-endpoints/{path_id('webhook_endpoint_id', webhook_endpoint_id)}",
                idempotency_key=idempotency_key,
            ),
        )

    def rotate_signing_secret(
        self,
        webhook_endpoint_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> RotateWebhookSigningSecretResponse:
        return cast(
            RotateWebhookSigningSecretResponse,
            self._request(
                "POST",
                "/v1/webhook-endpoints/"
                f"{path_id('webhook_endpoint_id', webhook_endpoint_id)}/rotate-signing-secret",
                idempotency_key=idempotency_key,
            ),
        )
