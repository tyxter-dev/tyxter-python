from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from uuid import uuid4

from tyxter import Tyxter, WebhookSignatureVerifier
from tyxter.types import MessageDetailResponse, MessageResponse, WebhookEventResponse


@dataclass(frozen=True)
class FirstMessageResult:
    message: MessageResponse
    detail: MessageDetailResponse
    webhook_event: WebhookEventResponse | None


def build_client() -> Tyxter:
    return Tyxter(
        api_key=os.environ["TYXTER_API_KEY"],
        base_url=os.environ.get("TYXTER_API_BASE_URL", "https://api.tyxter.com"),
    )


def send_sandbox_message(
    client: Tyxter,
    *,
    from_phone_number_id: str = "pn_sandbox",
    to: str,
    idempotency_key: str = "idem_python_quickstart_001",
) -> MessageResponse:
    return client.messages.send_text(
        {
            "channel": "whatsapp",
            "sender": {"type": "whatsapp_phone_number", "id": from_phone_number_id},
            "recipient": {"type": "phone_e164", "id": to},
            "text": {"body": "Hello from the Tyxter Python SDK."},
        },
        idempotency_key=idempotency_key,
    )


def verify_tyxter_webhook(
    *,
    raw_body: bytes,
    headers: Mapping[str, str],
    signing_secret: str,
    now: int | None = None,
) -> bool:
    return WebhookSignatureVerifier(signing_secret).verify(
        raw_body=raw_body,
        headers=headers,
        now=now,
    )


def send_inspect_and_verify(
    client: Tyxter,
    *,
    to: str,
    signing_secret: str | None = None,
    webhook_endpoint_id: str | None = None,
    from_phone_number_id: str = "pn_sandbox",
    idempotency_key: str = "idem_python_quickstart_001",
) -> FirstMessageResult:
    """Run the first-message loop using documented public /v1 routes only."""
    cursor: str | None = None
    event_types = "message.sent,message.delivered,message.failed"
    if signing_secret is not None:
        if webhook_endpoint_id is None:
            endpoints = client.webhook_endpoints.list(limit=100)["data"]
            active_endpoint_ids = [
                endpoint["id"] for endpoint in endpoints if endpoint["status"] == "active"
            ]
            if len(active_endpoint_ids) != 1:
                raise RuntimeError(
                    "set TYXTER_WEBHOOK_ENDPOINT_ID when the environment does not have "
                    "exactly one active webhook endpoint"
                )
            webhook_endpoint_id = active_endpoint_ids[0]
        tail = client.webhook_events.listen(
            limit=1,
            start_at="tail",
            event_types=event_types,
            webhook_endpoint_id=webhook_endpoint_id,
        )
        cursor = tail["next_cursor"]
        if cursor is None:
            raise RuntimeError("webhook listen tail did not return a checkpoint cursor")

    client.sandbox.inbound_messages.create(
        {
            "channel": "whatsapp",
            "from": to,
            "to": from_phone_number_id,
            "type": "text",
            "text": {"body": "Open the sandbox service window."},
        },
        idempotency_key=f"{idempotency_key}_inbound",
    )
    message = send_sandbox_message(
        client,
        from_phone_number_id=from_phone_number_id,
        to=to,
        idempotency_key=idempotency_key,
    )
    detail = client.messages.retrieve(message["id"])
    if signing_secret is None:
        return FirstMessageResult(message=message, detail=detail, webhook_event=None)

    for _ in range(5):
        events = client.webhook_events.listen(
            limit=100,
            cursor=cursor,
            event_types=event_types,
            wait_ms=5_000,
            webhook_endpoint_id=webhook_endpoint_id,
        )
        for event in events["data"]:
            if event["source_id"] != message["id"]:
                continue
            preview = event.get("signature_preview")
            if preview is None:
                raise RuntimeError("webhook event did not include a signature preview")
            if not verify_tyxter_webhook(
                raw_body=preview["raw_body"].encode("utf-8"),
                headers=preview["headers"],
                signing_secret=signing_secret,
                now=int(preview["timestamp"]),
            ):
                raise RuntimeError("webhook signature preview did not verify")
            return FirstMessageResult(message=message, detail=detail, webhook_event=event)
        cursor = events["next_cursor"]

    raise RuntimeError(f"no webhook event observed for message {message['id']}")


def main() -> None:
    with build_client() as client:
        from_phone_number_id = os.environ.get("TYXTER_FROM")
        if from_phone_number_id is None:
            from_phone_number_id = client.sandbox.quickstart()["sender"]["default_sender_id"]
        if from_phone_number_id is None:
            raise RuntimeError("sandbox quickstart did not return a default sender")
        result = send_inspect_and_verify(
            client,
            from_phone_number_id=from_phone_number_id,
            to=os.environ.get("TYXTER_TO", "+15555550100"),
            signing_secret=os.environ.get("TYXTER_WEBHOOK_SECRET"),
            webhook_endpoint_id=os.environ.get("TYXTER_WEBHOOK_ENDPOINT_ID"),
            idempotency_key=os.environ.get(
                "TYXTER_IDEMPOTENCY_KEY",
                f"idem_python_quickstart_{uuid4().hex}",
            ),
        )
    print(result.message["id"], result.detail["status"])
    if result.webhook_event is not None:
        print(result.webhook_event["type"], "signature verified")


if __name__ == "__main__":
    main()
