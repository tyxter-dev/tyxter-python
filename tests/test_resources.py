from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from tyxter import Tyxter


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
    return json.loads(request.read())


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

    result = client.messages.create(
        {"type": "text", "to": "+15555550100", "text": {"body": "hello"}},
        idempotency_key="idem_msg",
        trace_id="trc_sdk",
    )

    assert result == {"ok": True}
    request = seen[0]
    assert_request(
        request,
        method="POST",
        url="https://api.test/v1/messages",
        body={"type": "text", "to": "+15555550100", "text": {"body": "hello"}},
    )
    assert request.headers["idempotency-key"] == "idem_msg"
    assert request.headers["tyxter-trace-id"] == "trc_sdk"


def test_messages_list_filters_none_query_params() -> None:
    client, seen = make_client()

    client.messages.list(limit=25, starting_after=None, status="queued", batch_id="batch_123")

    assert_request(
        seen[0],
        method="GET",
        url="https://api.test/v1/messages?limit=25&status=queued&batch_id=batch_123",
    )


def test_messages_helpers_set_message_type() -> None:
    client, seen = make_client()

    client.messages.send_text({"to": "+15555550100", "text": {"body": "hello"}})

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/messages",
        body={"to": "+15555550100", "text": {"body": "hello"}, "type": "text"},
    )


def test_messages_get_escapes_message_id() -> None:
    client, seen = make_client()

    client.messages.get("msg/123")

    assert_request(seen[0], method="GET", url="https://api.test/v1/messages/msg%2F123")


def test_batches_resource_paths_and_payloads() -> None:
    client, seen = make_client()

    client.batches.create({"name": "launch", "recipients": [{"to": "+15555550100"}]})
    client.batches.get("batch_123")
    client.batches.pause("batch_123")
    client.batches.resume("batch_123")
    client.batches.cancel("batch_123")
    client.batches.failures("batch_123")
    client.batches.list(limit=10)

    assert_request(
        seen[0],
        method="POST",
        url="https://api.test/v1/batches",
        body={"name": "launch", "recipients": [{"to": "+15555550100"}]},
    )
    assert_request(seen[1], method="GET", url="https://api.test/v1/batches/batch_123")
    assert_request(
        seen[2],
        method="POST",
        url="https://api.test/v1/batches/batch_123/pause",
        body={},
    )
    assert_request(
        seen[3],
        method="POST",
        url="https://api.test/v1/batches/batch_123/resume",
        body={},
    )
    assert_request(
        seen[4],
        method="POST",
        url="https://api.test/v1/batches/batch_123/cancel",
        body={},
    )
    assert_request(seen[5], method="GET", url="https://api.test/v1/batches/batch_123/failures")
    assert_request(seen[6], method="GET", url="https://api.test/v1/batches?limit=10")


def test_contacts_resource_paths_and_payloads() -> None:
    client, seen = make_client()

    client.contacts.opt_in({"phone": "+15555550100"}, idempotency_key="idem_contact")
    client.contacts.opt_out({"phone": "+15555550100", "reason": "unsubscribe"})
    client.contacts.bulk_import({"rows": [{"phone": "+15555550100"}]}, trace_id="trc_bulk")
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
    assert seen[2].headers["tyxter-trace-id"] == "trc_bulk"
    assert_request(seen[3], method="GET", url="https://api.test/v1/contacts?limit=5&starting_after=ct_1")
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
        body={},
    )


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
    ],
)
def test_resource_ids_are_required(call: Callable[[Tyxter], object], message: str) -> None:
    client, _ = make_client()

    with pytest.raises(ValueError) as exc_info:
        call(client)

    assert str(exc_info.value) == message
