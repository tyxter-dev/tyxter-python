from __future__ import annotations

from typing import Literal, cast

from tyxter.types import (
    CreateMessageRequest,
    ListMessagesResponse,
    MessageDetailResponse,
    MessageDirection,
    MessageResponse,
    OutboundMessage,
    SendFlowMessageInput,
    SendInteractiveMessageInput,
    SendMediaMessageInput,
    SendTemplateMessageInput,
    SendTextMessageInput,
)

from ._base import Resource, path_id


class MessagesResource(Resource):
    def create(
        self,
        payload: CreateMessageRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return cast(
            MessageResponse,
            self._request(
                "POST",
                "/v1/messages",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def send_text(
        self,
        payload: SendTextMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self.create(
            _message_request(payload, {"type": "text", "text": payload["text"]}),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_template(
        self,
        payload: SendTemplateMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self.create(
            _message_request(payload, {"type": "template", "template": payload["template"]}),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_media(
        self,
        payload: SendMediaMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self.create(
            _message_request(payload, {"type": "media", "media": payload["media"]}),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_interactive(
        self,
        payload: SendInteractiveMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self.create(
            _message_request(
                payload,
                {"type": "interactive", "interactive": payload["interactive"]},
            ),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_flow(
        self,
        payload: SendFlowMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self.create(
            _message_request(payload, {"type": "flow", "flow": payload["flow"]}),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def get(self, message_id: str) -> MessageDetailResponse:
        return cast(
            MessageDetailResponse,
            self._request("GET", f"/v1/messages/{path_id('message_id', message_id)}"),
        )

    def retrieve(self, message_id: str) -> MessageDetailResponse:
        return self.get(message_id)

    def cancel(
        self,
        message_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> MessageDetailResponse:
        return cast(
            MessageDetailResponse,
            self._request(
                "POST",
                f"/v1/messages/{path_id('message_id', message_id)}/cancel",
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: str | None = None,
        batch_id: str | None = None,
        direction: MessageDirection | None = None,
        include: Literal["payload"] | None = None,
    ) -> ListMessagesResponse:
        return cast(
            ListMessagesResponse,
            self._request(
                "GET",
                "/v1/messages",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "status": status,
                    "batch_id": batch_id,
                    "direction": direction,
                    "include": include,
                },
            ),
        )


def _message_request(
    payload: (
        SendTextMessageInput
        | SendTemplateMessageInput
        | SendMediaMessageInput
        | SendInteractiveMessageInput
        | SendFlowMessageInput
    ),
    message: OutboundMessage,
) -> CreateMessageRequest:
    request: CreateMessageRequest = {
        "channel": payload["channel"],
        "sender": payload["sender"],
        "recipient": payload["recipient"],
        "message": message,
    }
    if "metadata" in payload:
        request["metadata"] = payload["metadata"]
    return request
