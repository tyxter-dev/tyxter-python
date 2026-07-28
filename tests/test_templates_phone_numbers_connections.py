from __future__ import annotations

import json
from typing import cast

import httpx

from tyxter import Tyxter


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def make_client(seen: list[httpx.Request]) -> Tyxter:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    return Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )


def test_templates_cover_all_routes_and_only_generate_is_idempotent() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.templates.create(
        {
            "name": "order_ready",
            "language": "en_US",
            "category": "utility",
            "components": [{"type": "BODY", "text": "Ready"}],
        }
    )
    client.templates.generate(
        {
            "description": "Tell a customer their order is ready",
            "language": "en_US",
            "category": "utility",
        },
        idempotency_key="idem_generate",
    )
    client.templates.list(limit=10, starting_after="tpl_1")
    client.templates.retrieve("tpl/2")
    client.templates.update("tpl/2", {"language": "pt_BR"})
    client.templates.submit("tpl/2")
    client.templates.duplicate("tpl/2")
    client.templates.analytics("tpl/2")
    client.templates.estimate_cost("tpl/2", {"recipients": 20})
    client.templates.delete("tpl/2")

    assert body(seen[0])["name"] == "order_ready"
    assert seen[1].headers["idempotency-key"] == "idem_generate"
    assert str(seen[2].url) == ("https://api.test/v1/templates?limit=10&starting_after=tpl_1")
    assert all("idempotency-key" not in request.headers for request in seen[2:])
    assert str(seen[3].url) == "https://api.test/v1/templates/tpl%2F2"
    assert body(seen[4]) == {"language": "pt_BR"}
    assert not seen[5].content
    assert body(seen[6]) == {}
    assert seen[7].url.path.endswith("/analytics")
    assert body(seen[8]) == {"recipients": 20}
    assert seen[9].method == "DELETE"


def test_phone_numbers_cover_lifecycle_and_escape_ids() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.phone_numbers.list(limit=10, status="active")
    client.phone_numbers.list_available_regions()
    client.phone_numbers.provision({"ddd": "11"}, idempotency_key="idem_provision")
    client.phone_numbers.connect(
        {"phone": "+5511999999999", "meta_phone_number_id": "meta_1"},
        idempotency_key="idem_connect",
    )
    client.phone_numbers.retrieve("pn/1")
    client.phone_numbers.release("pn/1", idempotency_key="idem_release")
    client.phone_numbers.transfer(
        "pn/1",
        {
            "source_project_id": "prj_a",
            "source_environment_id": "env_a",
            "target_project_id": "prj_b",
            "target_environment_id": "env_b",
            "confirm_phone_number_id": "pn/1",
        },
        idempotency_key="idem_transfer",
    )
    client.phone_numbers.disconnect("pn/1")

    assert seen[0].url.query.decode() == "limit=10&status=active"
    assert seen[1].url.path == "/v1/phone-numbers/available-regions"
    assert [seen[index].headers["idempotency-key"] for index in (2, 3, 5, 6)] == [
        "idem_provision",
        "idem_connect",
        "idem_release",
        "idem_transfer",
    ]
    assert str(seen[4].url) == "https://api.test/v1/phone-numbers/pn%2F1"
    assert not seen[5].content
    assert seen[7].method == "DELETE"


def test_provider_connections_and_credential_setup_match_header_capabilities() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.provider_connections.list(limit=5, starting_after="pc_1")
    client.provider_connections.status()
    client.provider_connections.meta_onboarding()
    client.provider_connections.register_meta(
        {"display_name": "Meta", "access_token": "token", "channel": "whatsapp"}
    )
    client.provider_connections.exchange_meta_oauth(
        {"code": "code", "waba_id": "waba", "phone_number_id": "phone"}
    )
    client.provider_connections.retrieve("pc/2")
    client.provider_connections.rotate_token("pc/2", {"access_token": "new"})
    client.provider_connections.delete("pc/2")
    client.provider_credential_setup_sessions.create(
        {"target": "meta.whatsapp"}, idempotency_key="idem_setup"
    )
    client.provider_credential_setup_sessions.retrieve("req/1")
    client.provider_connections.complete_meta_registration("pc/2", idempotency_key="idem_complete")

    assert seen[0].url.query.decode() == "limit=5&starting_after=pc_1"
    assert seen[1].url.path.endswith("/status")
    assert seen[2].url.path.endswith("/meta/onboarding")
    assert body(seen[3])["access_token"] == "token"
    assert all("idempotency-key" not in request.headers for request in seen[:8])
    assert str(seen[5].url) == "https://api.test/v1/provider-connections/pc%2F2"
    assert body(seen[6]) == {"access_token": "new"}
    assert seen[7].method == "DELETE"
    assert seen[8].headers["idempotency-key"] == "idem_setup"
    assert str(seen[9].url) == ("https://api.test/v1/provider-credential-setup-sessions/req%2F1")
    assert seen[10].method == "POST"
    assert str(seen[10].url) == (
        "https://api.test/v1/provider-connections/pc%2F2/meta/complete-registration"
    )
    assert seen[10].headers["idempotency-key"] == "idem_complete"


def test_meta_signup_sessions_cover_create_and_poll() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.meta_signup_sessions.create(
        {
            "return_url": "https://merchant.example/meta/callback",
            "end_customer_ref": "customer_123",
        },
        idempotency_key="idem_meta_signup",
    )
    client.meta_signup_sessions.retrieve("mss/123")

    assert seen[0].method == "POST"
    assert str(seen[0].url) == "https://api.test/v1/meta-signup-sessions"
    assert seen[0].headers["idempotency-key"] == "idem_meta_signup"
    assert body(seen[0]) == {
        "return_url": "https://merchant.example/meta/callback",
        "end_customer_ref": "customer_123",
    }
    assert seen[1].method == "GET"
    assert str(seen[1].url) == "https://api.test/v1/meta-signup-sessions/mss%2F123"


def test_audiences_cover_crud_without_stale_js_headers() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.audiences.create({"name": "Customers", "contact_ids": ["ct_1"]})
    client.audiences.list(limit=5, starting_after="aud_1")
    client.audiences.retrieve("aud/2")
    client.audiences.update("aud/2", {"description": "Active customers"})
    client.audiences.delete("aud/2")

    assert body(seen[0]) == {"name": "Customers", "contact_ids": ["ct_1"]}
    assert str(seen[1].url) == ("https://api.test/v1/audiences?limit=5&starting_after=aud_1")
    assert str(seen[2].url) == "https://api.test/v1/audiences/aud%2F2"
    assert body(seen[3]) == {"description": "Active customers"}
    assert seen[4].method == "DELETE"
    assert all("idempotency-key" not in request.headers for request in seen)
    assert all("tyxter-trace-id" not in request.headers for request in seen)
