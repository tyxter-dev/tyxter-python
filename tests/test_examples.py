from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import httpx

from tyxter import Tyxter, sign_webhook


def load_example() -> ModuleType:
    example_path = Path(__file__).parents[1] / "examples" / "sandbox_send_and_verify.py"
    spec = importlib.util.spec_from_file_location("sandbox_send_and_verify", example_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"failed to load example from {example_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sandbox_sender_example_uses_public_messages_api() -> None:
    example = load_example()
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
    example = load_example()
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
