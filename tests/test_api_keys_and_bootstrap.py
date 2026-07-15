from __future__ import annotations

import json
from typing import cast

import httpx

from tyxter import Tyxter, TyxterBootstrap


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def test_api_keys_match_manifest_routes_and_header_capabilities() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.api_keys.create(
        {"name": "Agent", "environment": "sandbox", "scopes": ["messages:write"]},
        idempotency_key="idem_key",
    )
    client.api_keys.list(limit=10, starting_after="key_1")
    client.api_keys.retrieve("key/2")
    client.api_keys.rename("key/2", {"name": "Renamed agent"})
    client.api_keys.rotate("key/2")
    client.api_keys.revoke("key/2")

    assert seen[0].headers["idempotency-key"] == "idem_key"
    assert seen[0].headers["authorization"] == "Bearer tx_sandbox_test"
    assert seen[1].url.query.decode() == "limit=10&starting_after=key_1"
    assert str(seen[2].url) == "https://api.test/v1/api-keys/key%2F2"
    assert body(seen[3]) == {"name": "Renamed agent"}
    assert not seen[4].content
    assert seen[5].method == "DELETE"
    assert all("idempotency-key" not in request.headers for request in seen[1:])


def test_device_bootstrap_is_unauthenticated_and_traceable() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"status": "pending"})

    client = TyxterBootstrap(base_url="https://api.test", transport=httpx.MockTransport(handler))

    client.agent_api_key_device_authorizations.create(
        {
            "client_name": "Codex",
            "environment": "sandbox",
            "scopes": ["messages:write"],
        },
        trace_id="trc_bootstrap",
    )
    client.agent_api_key_device_authorizations.token(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": "device_1",
        },
        trace_id="trc_poll",
    )

    assert [request.url.path for request in seen] == [
        "/v1/agent-api-key-device-authorizations",
        "/v1/agent-api-key-device-authorizations/token",
    ]
    assert all("authorization" not in request.headers for request in seen)
    assert seen[0].headers["tyxter-trace-id"] == "trc_bootstrap"
    assert seen[1].headers["tyxter-trace-id"] == "trc_poll"
    assert body(seen[1])["device_code"] == "device_1"
