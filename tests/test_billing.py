from __future__ import annotations

import json
from typing import cast

import httpx

from tyxter import Tyxter


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def test_billing_covers_manifest_routes_and_headers() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.billing.balance()
    client.billing.list_plans()
    client.billing.current_plan()
    client.billing.subscribe_plan({"plan_offering_id": "growth"}, idempotency_key="idem_subscribe")
    client.billing.change_plan({"plan_offering_id": "scale"}, idempotency_key="idem_change")
    client.billing.cancel_plan(idempotency_key="idem_cancel")
    client.billing.list_packages(limit=10, status="succeeded")
    client.billing.purchase_package(
        {"package_code": "pkg_10k", "payment_method": "pix"},
        idempotency_key="idem_purchase",
    )
    client.billing.list_payment_methods()
    client.billing.save_payment_method({"payment_method_id": "pm_1"}, idempotency_key="idem_save")
    client.billing.create_payment_method_setup_intent(idempotency_key="idem_setup")
    client.billing.set_default_payment_method("pm/1", idempotency_key="idem_default")
    client.billing.delete_payment_method("pm/1", idempotency_key="idem_delete")
    client.billing.retrieve_auto_topup()
    client.billing.update_auto_topup({"enabled": True}, idempotency_key="idem_auto")
    client.billing.list_ledger(environment="sandbox", source_type="usage")
    client.billing.list_invoices(project_id="prj_1")
    client.billing.download_invoice("inv/1")
    client.rate_cards.list(limit=5, currency="brl")
    client.rate_cards.retrieve_current()

    assert body(seen[3]) == {"plan_offering_id": "growth"}
    assert not seen[5].content
    assert seen[6].url.query.decode() == "limit=10&status=succeeded"
    assert not seen[10].content
    assert str(seen[11].url).endswith("/payment-methods/pm%2F1/default")
    assert str(seen[12].url).endswith("/payment-methods/pm%2F1")
    assert seen[15].url.query.decode() == "environment=sandbox&source_type=usage"
    assert seen[16].url.query.decode() == "project_id=prj_1"
    assert str(seen[17].url).endswith("/invoices/inv%2F1/download")
    assert seen[18].url.query.decode() == "limit=5&currency=brl"
    expected_idempotency = {
        3: "idem_subscribe",
        4: "idem_change",
        5: "idem_cancel",
        7: "idem_purchase",
        9: "idem_save",
        10: "idem_setup",
        11: "idem_default",
        12: "idem_delete",
        14: "idem_auto",
    }
    assert {
        index: request.headers["idempotency-key"]
        for index, request in enumerate(seen)
        if "idempotency-key" in request.headers
    } == expected_idempotency
