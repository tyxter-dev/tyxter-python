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


def test_flows_fiscal_and_feedback_cover_public_routes() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.flows.create({"name": "checkout", "flow_json": {"version": "1"}})
    client.flows.list(limit=10, starting_after="flow_1")
    client.flows.retrieve("flow/2")
    client.flows.publish("flow/2", idempotency_key="idem_publish")
    client.fiscal.list_nfse(status="authorized", source_kind="consumption_period")
    client.fiscal.get_nfse("nfse/1")
    client.fiscal.download_danfse("nfse/1")
    client.fiscal.download_xml("nfse/1")
    client.feedback.create(
        {
            "message": "Unexpected response",
            "related_error": {"code": "provider_error"},
            "context": {"operation": "messages.create"},
        },
        idempotency_key="idem_feedback",
        trace_id="trc_feedback",
    )

    assert body(seen[0]) == {"name": "checkout", "flow_json": {"version": "1"}}
    assert seen[1].url.query.decode() == "limit=10&starting_after=flow_1"
    assert str(seen[2].url).endswith("/flows/flow%2F2")
    assert not seen[3].content
    assert seen[3].headers["idempotency-key"] == "idem_publish"
    assert seen[4].url.query.decode() == ("status=authorized&source_kind=consumption_period")
    assert str(seen[5].url).endswith("/fiscal/nfse/nfse%2F1")
    assert str(seen[6].url).endswith("/fiscal/nfse/nfse%2F1/danfse")
    assert str(seen[7].url).endswith("/fiscal/nfse/nfse%2F1/xml")
    assert seen[8].headers["idempotency-key"] == "idem_feedback"
    assert seen[8].headers["tyxter-trace-id"] == "trc_feedback"


def test_llm_routes_and_completions_cover_queries_and_headers() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.llm_routes.upsert(
        {
            "provider": "openai",
            "model": "gpt-test",
            "api_key": "secret-value",
            "system_prompt": "You are a helpful assistant for this messaging business.",
        }
    )
    client.llm_routes.retrieve(phone_number_id="pn_1")
    client.llm_routes.update({"enabled": False}, phone_number_id="pn_1")
    client.llm_routes.list_prompt_versions(limit=5, phone_number_id="pn_1")
    client.llm_routes.delete(phone_number_id="pn_1")
    client.llm.complete(
        {"messages": [{"role": "user", "content": "Hello"}]},
        idempotency_key="idem_llm",
        trace_id="trc_llm",
    )
    client.llm.list_responses(limit=10, starting_after="log_1")

    assert body(seen[0])["provider"] == "openai"
    assert seen[1].url.query.decode() == "phone_number_id=pn_1"
    assert body(seen[2]) == {"enabled": False}
    assert seen[2].url.query.decode() == "phone_number_id=pn_1"
    assert seen[3].url.query.decode() == "limit=5&phone_number_id=pn_1"
    assert seen[4].method == "DELETE"
    assert seen[5].headers["idempotency-key"] == "idem_llm"
    assert seen[5].headers["tyxter-trace-id"] == "trc_llm"
    assert seen[6].url.query.decode() == "limit=10&starting_after=log_1"


def test_agentic_payments_cover_banks_authorizations_and_payments() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.agentic_payments.list_banks(search="bank", limit=20)
    client.agentic_payments.create_authorization(
        {"customer_tax_id": "12345678901", "agent_reason": "Pay invoice"},
        idempotency_key="idem_auth",
        trace_id="trc_auth",
    )
    client.agentic_payments.list_authorizations(status="completed", customer_tax_id="12345678901")
    client.agentic_payments.retrieve_authorization("auth/1")
    client.agentic_payments.revoke_authorization(
        "auth/1", idempotency_key="idem_revoke", trace_id="trc_revoke"
    )
    client.agentic_payments.create_payment(
        {
            "amount_brl_centavos": 1000,
            "method": "PIX_DICT",
            "customer_tax_id": "12345678901",
            "agent_reason": "Pay invoice",
            "pix_key": "pix@example.com",
        },
        idempotency_key="idem_payment",
        trace_id="trc_payment",
    )
    client.agentic_payments.list_payments(status="paid", starting_after="pay_1")
    client.agentic_payments.retrieve_payment("pay/2")
    client.agentic_payments.cancel_payment(
        "pay/2", idempotency_key="idem_cancel", trace_id="trc_cancel"
    )

    assert seen[0].url.query.decode() == "search=bank&limit=20"
    assert seen[1].headers["idempotency-key"] == "idem_auth"
    assert seen[1].headers["tyxter-trace-id"] == "trc_auth"
    assert seen[2].url.query.decode() == ("status=completed&customer_tax_id=12345678901")
    assert str(seen[3].url).endswith("/agentic/authorizations/auth%2F1")
    assert not seen[4].content
    assert seen[4].headers["idempotency-key"] == "idem_revoke"
    assert body(seen[5])["pix_key"] == "pix@example.com"
    assert seen[5].headers["tyxter-trace-id"] == "trc_payment"
    assert seen[6].url.query.decode() == "starting_after=pay_1&status=paid"
    assert str(seen[7].url).endswith("/agentic/payments/pay%2F2")
    assert not seen[8].content
    assert seen[8].headers["idempotency-key"] == "idem_cancel"


def test_data_retention_covers_policy_read_and_update() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.data_retention.retrieve()
    client.data_retention.update(
        {"retention_days": 30, "data_export_enabled": False},
        idempotency_key="idem_retention",
    )

    assert [(request.method, request.url.path) for request in seen] == [
        ("GET", "/v1/data-retention"),
        ("PATCH", "/v1/data-retention"),
    ]
    assert body(seen[1]) == {"retention_days": 30, "data_export_enabled": False}
    assert "idempotency-key" not in seen[0].headers
    assert seen[1].headers["idempotency-key"] == "idem_retention"
