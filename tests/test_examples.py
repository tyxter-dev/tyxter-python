from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import httpx
import pytest

from tyxter import Tyxter, sign_webhook


def load_example(name: str) -> ModuleType:
    example_path = Path(__file__).parents[1] / "examples" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, example_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"failed to load example from {example_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_sandbox_sender_example_uses_public_messages_api() -> None:
    example = load_example("sandbox_send_and_verify")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"id": "msg_123", "object": "message"})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    result = example.send_sandbox_message(client, to="+15555550100")

    assert result["id"] == "msg_123"
    assert len(seen) == 1
    request = seen[0]
    assert request.method == "POST"
    assert request.url.path == "/v1/messages"
    assert not request.url.path.startswith("/dashboard-bff")
    assert "/internal" not in request.url.path
    assert "/providers/" not in request.url.path


def test_webhook_verifier_example_uses_public_signature_helper() -> None:
    example = load_example("sandbox_send_and_verify")
    secret = "wh_secret_abcdef"
    timestamp = "1714123456"
    raw_body = b'{"type":"message.sent","id":"msg_1"}'
    signature = sign_webhook(secret, timestamp, raw_body)

    assert example.verify_tyxter_webhook(
        raw_body=raw_body,
        headers={
            "tyxter-webhook-timestamp": timestamp,
            "tyxter-webhook-signature": signature,
        },
        signing_secret=secret,
        now=int(timestamp),
    )


def test_first_message_example_sends_inspects_and_verifies_public_webhook() -> None:
    example = load_example("sandbox_send_and_verify")
    seen: list[httpx.Request] = []
    secret = "wh_secret_abcdef"
    timestamp = "1714123456"
    raw_body = '{"id":"evt_1","type":"message.sent"}'
    signature = sign_webhook(secret, timestamp, raw_body)
    listen_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal listen_calls
        seen.append(request)
        if request.url.path == "/v1/webhook-endpoints":
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [{"id": "whe_1", "status": "active"}],
                    "has_more": False,
                    "next_cursor": None,
                },
            )
        if request.url.path == "/v1/webhook-events/listen":
            listen_calls += 1
            if listen_calls == 1:
                assert request.url.params["start_at"] == "tail"
                assert request.url.params["webhook_endpoint_id"] == "whe_1"
                return httpx.Response(
                    200,
                    json={
                        "object": "webhook_event_listen",
                        "data": [],
                        "has_more": False,
                        "next_cursor": "cur_tail",
                    },
                )
            assert request.url.params["cursor"] == "cur_tail"
            assert request.url.params["webhook_endpoint_id"] == "whe_1"
            return httpx.Response(
                200,
                json={
                    "object": "webhook_event_listen",
                    "data": [
                        {
                            "id": "evt_1",
                            "object": "webhook_event",
                            "source_id": "msg_123",
                            "type": "message.sent",
                            "signature_preview": {
                                "raw_body": raw_body,
                                "timestamp": timestamp,
                                "headers": {
                                    "tyxter-webhook-timestamp": timestamp,
                                    "tyxter-webhook-signature": signature,
                                },
                            },
                        }
                    ],
                    "has_more": False,
                    "next_cursor": None,
                },
            )
        if request.url.path == "/v1/sandbox/inbound-messages":
            return httpx.Response(
                202,
                json={"id": "msg_inbound", "object": "message", "status": "received"},
            )
        if request.url.path == "/v1/messages" and request.method == "POST":
            return httpx.Response(
                202,
                json={"id": "msg_123", "object": "message", "status": "accepted"},
            )
        if request.url.path == "/v1/messages/msg_123":
            return httpx.Response(
                200,
                json={"id": "msg_123", "object": "message", "status": "sent"},
            )
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    result = example.send_inspect_and_verify(client, to="+15555550100", signing_secret=secret)

    assert result.message["id"] == "msg_123"
    assert result.detail["status"] == "sent"
    assert result.webhook_event["id"] == "evt_1"
    assert [request.url.path for request in seen] == [
        "/v1/webhook-endpoints",
        "/v1/webhook-events/listen",
        "/v1/sandbox/inbound-messages",
        "/v1/messages",
        "/v1/messages/msg_123",
        "/v1/webhook-events/listen",
    ]


def test_broadcast_demo_reads_customer_csv() -> None:
    example = load_example("broadcast_customer_list")
    customers_path = Path(__file__).parents[1] / "examples" / "customers.csv"

    customers = example.read_customer_list(customers_path)

    assert customers == [
        example.Customer(
            phone="+15555550100",
            variables={
                "full_name": "Ana Gomez",
                "external_id": "cus_001",
                "coupon_code": "SPRING10",
            },
        ),
        example.Customer(
            phone="+15555550101",
            variables={
                "full_name": "Diego Silva",
                "external_id": "cus_002",
                "coupon_code": "SPRING10",
            },
        ),
        example.Customer(
            phone="+15555550102",
            variables={
                "full_name": "Sam Lee",
                "external_id": "cus_003",
                "coupon_code": "SPRING10",
            },
        ),
    ]


def test_broadcast_demo_validates_phone_before_calling_sdk(tmp_path: Path) -> None:
    example = load_example("broadcast_customer_list")
    csv_path = tmp_path / "bad-customers.csv"
    csv_path.write_text("phone,full_name\nnot-a-phone,Ana\n", encoding="utf-8")

    with pytest.raises(ValueError) as exc_info:
        example.read_customer_list(csv_path)

    assert str(exc_info.value) == "row 2: phone must be E.164, e.g. +5511999999999"


def test_broadcast_demo_uses_public_batches_api() -> None:
    example = load_example("broadcast_customer_list")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            202,
            json={"id": "batch_123", "object": "message_batch", "trace_id": "trc_123"},
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    result = example.send_broadcast(
        client,
        customers=[
            example.Customer(phone="+15555550100", variables={"full_name": "Ana"}),
            example.Customer(phone="+15555550101", variables={}),
        ],
        from_phone_number_id="pn_123",
        template_name="promo_april",
        template_language="en_US",
        batch_name="April promo",
        idempotency_key="idem_broadcast_001",
    )

    assert result["id"] == "batch_123"
    assert len(seen) == 1
    request = seen[0]
    assert request.method == "POST"
    assert request.url.path == "/v1/batches"
    assert request.headers["idempotency-key"] == "idem_broadcast_001"
    assert not request.url.path.startswith("/dashboard-bff")
    assert "/internal" not in request.url.path
    assert "/providers/" not in request.url.path
    assert json.loads(request.read()) == {
        "channel": "whatsapp",
        "from": "pn_123",
        "template": {"name": "promo_april", "language": "en_US"},
        "recipients": [
            {"to": "+15555550100", "variables": {"full_name": "Ana"}},
            {"to": "+15555550101"},
        ],
        "name": "April promo",
    }
