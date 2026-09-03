from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, cast

import httpx
import pytest

from tyxter import Tyxter, TyxterAPIError
from tyxter.types import InteractiveMessagePayload, NativePixOrderDetailsMessagePayload


def make_client() -> tuple[Tyxter, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    return client, seen


def request_json(request: httpx.Request) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(request.read()))


def assert_request(
    request: httpx.Request,
    *,
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
) -> None:
    assert request.method == method
    assert str(request.url) == url
    if body is not None:
        assert request_json(request) == body


def test_messages_create_posts_payload_with_idempotency_and_trace_headers() -> None:
    client, seen = make_client()

    client.messages.create(
        {
            "channel": "whatsapp",
            "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
            "recipient": {"type": "phone_e164", "id": "+15555550100"},
            "message": {"type": "text", "text": {"body": "hello"}},
        },
        idempotency_key="idem_msg",
        trace_id="trc_sdk",
    )

    request = seen[0]
    assert_request(
        request,
        method="POST",
        url="https://api.test/v1/messages",
        body={
            "channel": "whatsapp",
            "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
            "recipient": {"type": "phone_e164", "id": "+15555550100"},
            "message": {"type": "text", "text": {"body": "hello"}},
        },
    )
    assert request.headers["idempotency-key"] == "idem_msg"
    assert request.headers["tyxter-trace-id"] == "trc_sdk"


def test_messages_list_filters_none_query_params() -> None:
    client, seen = make_client()

    client.messages.list(limit=25, starting_after=None, status="queued", batch_id="batch_123")
    client.messages.list(direction="inbound", include="payload")

    assert_request(
        seen[0],
        method="GET",
        url="https://api.test/v1/messages?limit=25&status=queued&batch_id=batch_123",
    )
    assert_request(
        seen[1],
        method="GET",
        url="https://api.test/v1/messages?direction=inbound&include=payload",
    )


def test_messages_helpers_set_message_type() -> None:
    client, seen = make_client()

    client.messages.send_text(
        {
            "channel": "whatsapp",
            "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
            "recipient": {"type": "phone_e164", "id": "+15555550100"},
            "text": {"body": "hello"},
        }
    )

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/messages",
        body={
            "channel": "whatsapp",
            "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
            "recipient": {"type": "phone_e164", "id": "+15555550100"},
            "message": {"type": "text", "text": {"body": "hello"}},
        },
    )


def test_messages_get_escapes_message_id() -> None:
    client, seen = make_client()

    client.messages.get("msg/123")
    client.messages.cancel("msg/123")

    assert_request(seen[0], method="GET", url="https://api.test/v1/messages/msg%2F123")
    assert_request(
        seen[1],
        method="POST",
        url="https://api.test/v1/messages/msg%2F123/cancel",
    )


def test_messages_transcription_and_typing_use_encoded_paths_and_trace_headers() -> None:
    client, seen = make_client()

    client.messages.request_transcription(
        "msg/123",
        {"language": "pt"},
        trace_id="trc_transcription",
    )
    client.messages.retrieve_transcription("msg/123", trace_id="trc_retrieve")
    client.messages.typing("msg/123", trace_id="trc_typing")

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/messages/msg%2F123/transcription",
        body={"language": "pt"},
    )
    assert seen[0].headers["tyxter-trace-id"] == "trc_transcription"
    assert "idempotency-key" not in seen[0].headers
    assert_request(
        seen[1],
        method="GET",
        url="https://api.test/v1/messages/msg%2F123/transcription",
    )
    assert seen[1].headers["tyxter-trace-id"] == "trc_retrieve"
    assert_request(
        seen[2],
        method="POST",
        url="https://api.test/v1/messages/msg%2F123/typing",
    )
    assert seen[2].headers["tyxter-trace-id"] == "trc_typing"
    assert "idempotency-key" not in seen[2].headers


def test_messages_retry_transcription_requires_and_trims_idempotency_key() -> None:
    client, seen = make_client()

    client.messages.retry_transcription(
        "msg/123",
        {"language": "pt"},
        idempotency_key="  idem_retry  ",
        trace_id="trc_retry",
    )

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/messages/msg%2F123/transcription/retry",
        body={"language": "pt"},
    )
    assert seen[0].headers["idempotency-key"] == "idem_retry"
    assert seen[0].headers["tyxter-trace-id"] == "trc_retry"


@pytest.mark.parametrize("idempotency_key", ["", " \t "])
def test_messages_retry_transcription_rejects_blank_keys_before_network_io(
    idempotency_key: str,
) -> None:
    client, seen = make_client()

    with pytest.raises(ValueError, match="idempotency_key must be a non-blank string"):
        client.messages.retry_transcription(
            "msg_123",
            {"language": "pt"},
            idempotency_key=idempotency_key,
        )

    assert seen == []


def test_messages_retry_transcription_preserves_retry_after_api_errors() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            429,
            json={
                "error": {
                    "type": "rate_limited",
                    "code": "transcription_retry_rate_limited",
                    "message": "Retry later",
                    "retry_after_ms": 250,
                }
            },
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TyxterAPIError) as exc_info:
        client.messages.retry_transcription(
            "msg_123",
            {"language": "pt"},
            idempotency_key="idem_retry",
        )

    assert exc_info.value.code == "transcription_retry_rate_limited"
    assert exc_info.value.retry_after_ms == 250
    assert seen[0].headers["idempotency-key"] == "idem_retry"


def test_whatsapp_builders_preserve_structured_recipients_and_native_pix() -> None:
    client, seen = make_client()
    order_details: NativePixOrderDetailsMessagePayload = {
        "type": "order_details",
        "header": {"type": "image", "link": "https://cdn.example.test/order.png"},
        "body": {"text": "Review your order"},
        "footer": {"text": "Tyxter Store"},
        "action": {
            "name": "review_and_pay",
            "parameters": {
                "reference_id": "order_123",
                "type": "physical-goods",
                "payment_type": "br",
                "payment_settings": (
                    {
                        "type": "pix_dynamic_code",
                        "pix_dynamic_code": {
                            "code": "000201010212",
                            "merchant_name": "Tyxter Store",
                            "key": "merchant@example.com",
                            "key_type": "EMAIL",
                        },
                    },
                ),
                "currency": "BRL",
                "total_amount": {"value": 12990, "offset": 100},
            },
        },
    }

    client.whatsapp.send_text(
        {
            "from": "pn_123",
            "to": {"country_calling_code": "55", "national_number": "11999999999"},
            "body": "Hello",
        }
    )
    client.whatsapp.send_interactive(
        {
            "from": "pn_123",
            "to": "+5511999999999",
            "interactive": order_details,
        }
    )

    assert request_json(seen[0])["recipient"] == {
        "type": "phone_e164",
        "country_calling_code": "55",
        "national_number": "11999999999",
    }
    interactive = request_json(seen[1])["message"]["interactive"]
    assert interactive["type"] == "order_details"
    assert interactive["header"] == {"type": "image", "link": "https://cdn.example.test/order.png"}
    assert interactive["body"] == {"text": "Review your order"}
    assert interactive["footer"] == {"text": "Tyxter Store"}
    assert interactive["action"]["parameters"]["payment_settings"] == [
        {
            "type": "pix_dynamic_code",
            "pix_dynamic_code": {
                "code": "000201010212",
                "merchant_name": "Tyxter Store",
                "key": "merchant@example.com",
                "key_type": "EMAIL",
            },
        }
    ]


def test_interactive_message_payload_remains_runtime_callable() -> None:
    payload = InteractiveMessagePayload(
        type="button",
        body={"text": "Choose one"},
        action={"buttons": [{"type": "reply", "reply": {"id": "one", "title": "One"}}]},
    )

    assert payload["type"] == "button"


def test_batches_resource_paths_and_payloads() -> None:
    client, seen = make_client()

    client.batches.create(
        {
            "channel": "whatsapp",
            "from": "pn_123",
            "template": {"name": "launch", "language": "en_US"},
            "name": "launch",
            "recipients": [{"to": "+15555550100"}],
        }
    )
    client.batches.get("batch_123", trace_id="trc_batch")
    client.batches.pause("batch_123", trace_id="trc_batch")
    client.batches.resume("batch_123", trace_id="trc_batch")
    client.batches.cancel("batch_123", trace_id="trc_batch")
    client.batches.failures("batch_123", trace_id="trc_batch")
    client.batches.list(limit=10, trace_id="trc_batch")

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/batches",
        body={
            "channel": "whatsapp",
            "from": "pn_123",
            "template": {"name": "launch", "language": "en_US"},
            "name": "launch",
            "recipients": [{"to": "+15555550100"}],
        },
    )
    assert_request(seen[1], method="GET", url="https://api.test/v1/batches/batch_123")
    assert_request(
        seen[2],
        method="POST",
        url="https://api.test/v1/batches/batch_123/pause",
    )
    assert_request(
        seen[3],
        method="POST",
        url="https://api.test/v1/batches/batch_123/resume",
    )
    assert_request(
        seen[4],
        method="POST",
        url="https://api.test/v1/batches/batch_123/cancel",
    )
    assert_request(seen[5], method="GET", url="https://api.test/v1/batches/batch_123/failures")
    assert_request(seen[6], method="GET", url="https://api.test/v1/batches?limit=10")
    for request in seen[1:]:
        assert request.headers["tyxter-trace-id"] == "trc_batch"


def test_contacts_resource_paths_and_payloads() -> None:
    client, seen = make_client()

    client.contacts.opt_in({"phone": "+15555550100"}, idempotency_key="idem_contact")
    client.contacts.opt_out({"phone": "+15555550100", "reason": "unsubscribe"})
    client.contacts.bulk_import({"rows": [{"phone": "+15555550100"}]})
    client.contacts.list(limit=5, starting_after="ct_1")
    client.contacts.export("ct_123")
    client.contacts.erase("ct_123")

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/contacts/opt-in",
        body={"phone": "+15555550100"},
    )
    assert seen[0].headers["idempotency-key"] == "idem_contact"
    assert_request(
        seen[1],
        method="POST",
        url="https://api.test/v1/contacts/opt-out",
        body={"phone": "+15555550100", "reason": "unsubscribe"},
    )
    assert_request(
        seen[2],
        method="POST",
        url="https://api.test/v1/contacts/bulk-import",
        body={"rows": [{"phone": "+15555550100"}]},
    )
    assert_request(
        seen[3], method="GET", url="https://api.test/v1/contacts?limit=5&starting_after=ct_1"
    )
    assert_request(seen[4], method="POST", url="https://api.test/v1/contacts/ct_123/export")
    assert_request(seen[5], method="DELETE", url="https://api.test/v1/contacts/ct_123")


def test_webhook_endpoints_resource_paths_and_payloads() -> None:
    client, seen = make_client()

    client.webhook_endpoints.create(
        {"url": "https://example.com/webhooks", "subscribed_events": ["message.sent"]},
        idempotency_key="idem_webhook",
    )
    client.webhook_endpoints.list(limit=3, starting_after="whe_1")
    client.webhook_endpoints.get("whe_123")
    client.webhook_endpoints.update("whe_123", {"status": "disabled"})
    client.webhook_endpoints.delete("whe_123")
    client.webhook_endpoints.rotate_signing_secret("whe_123")

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/webhook-endpoints",
        body={"url": "https://example.com/webhooks", "subscribed_events": ["message.sent"]},
    )
    assert seen[0].headers["idempotency-key"] == "idem_webhook"
    assert_request(
        seen[1],
        method="GET",
        url="https://api.test/v1/webhook-endpoints?limit=3&starting_after=whe_1",
    )
    assert_request(seen[2], method="GET", url="https://api.test/v1/webhook-endpoints/whe_123")
    assert_request(
        seen[3],
        method="PATCH",
        url="https://api.test/v1/webhook-endpoints/whe_123",
        body={"status": "disabled"},
    )
    assert_request(seen[4], method="DELETE", url="https://api.test/v1/webhook-endpoints/whe_123")
    assert_request(
        seen[5],
        method="POST",
        url="https://api.test/v1/webhook-endpoints/whe_123/rotate-signing-secret",
    )


def test_webhook_endpoint_test_is_an_empty_body_supported_idempotent_post() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "object": "webhook_test",
                "webhook_event_id": "wev_1",
                "webhook_endpoint_id": "whe_1",
                "status": "pending",
            },
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    receipt = client.webhook_endpoints.test("whe/1", idempotency_key="idem_webhook_test")

    assert receipt["status"] == "pending"
    assert str(seen[0].url) == "https://api.test/v1/webhook-endpoints/whe%2F1/test"
    assert not seen[0].content
    assert "content-type" not in seen[0].headers
    assert seen[0].headers["idempotency-key"] == "idem_webhook_test"
    assert "tyxter-trace-id" not in seen[0].headers


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda client: client.messages.get(""), "message_id is required"),
        (lambda client: client.batches.get(""), "batch_id is required"),
        (lambda client: client.contacts.erase(""), "contact_id is required"),
        (
            lambda client: client.webhook_endpoints.get(""),
            "webhook_endpoint_id is required",
        ),
        (lambda client: client.webhook_endpoints.test(""), "webhook_endpoint_id is required"),
        (lambda client: client.feedback.get(""), "feedback_report_id is required"),
        (lambda client: client.projects.retrieve(""), "project_id is required"),
        (lambda client: client.billing.retrieve_phone_renewal(""), "cycle_id is required"),
    ],
)
def test_resource_ids_are_required(call: Callable[[Tyxter], object], message: str) -> None:
    client, _ = make_client()

    with pytest.raises(ValueError) as exc_info:
        call(client)

    assert str(exc_info.value) == message
