from __future__ import annotations

import json
from typing import cast

import httpx

from tyxter import Tyxter
from tyxter.types import AutomationGraph


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


def test_ai_agents_cover_all_routes_with_manifest_headers() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.ai_agents.create(
        {
            "name": "Support",
            "provider": "openai",
            "model": "gpt-test",
            "api_key": "secret-value",
            "system_prompt": "You are a helpful customer support agent for this business.",
        },
        idempotency_key="idem_agent",
    )
    client.ai_agents.list(limit=10, include_archived=True)
    client.ai_agents.retrieve("agent/1")
    client.ai_agents.update("agent/1", {"enabled": False})
    client.ai_agents.complete(
        "agent/1",
        {"messages": [{"role": "user", "content": "Hello"}]},
        idempotency_key="idem_ai_completion",
        trace_id="trc_completion",
    )
    client.ai_agents.list_prompt_versions("agent/1", limit=5)
    client.ai_agents.list_response_logs("agent/1", starting_after="log_1")
    client.ai_agents.delete("agent/1")

    assert seen[0].headers["idempotency-key"] == "idem_agent"
    assert seen[1].url.query.decode() == "limit=10&include_archived=true"
    assert str(seen[2].url) == "https://api.test/v1/ai-agents/agent%2F1"
    assert body(seen[3]) == {"enabled": False}
    assert seen[4].headers["tyxter-trace-id"] == "trc_completion"
    assert seen[4].headers["idempotency-key"] == "idem_ai_completion"
    assert body(seen[4])["messages"] == [{"role": "user", "content": "Hello"}]
    assert seen[5].url.query.decode() == "limit=5"
    assert seen[6].url.query.decode() == "starting_after=log_1"
    assert seen[7].method == "DELETE"


def test_automations_cover_crud_versions_runs_and_webhooks() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)
    graph: AutomationGraph = {
        "version": "automation_graph_v1",
        "nodes": [{"id": "trigger", "type": "manual.trigger", "config": {}}],
        "edges": [],
    }

    client.automations.create({"name": "Welcome"}, idempotency_key="idem_create")
    client.automations.list(limit=10, status="active")
    client.automations.retrieve("auto/1")
    client.automations.update("auto/1", {"description": "Welcome flow"})
    client.automations.create_version("auto/1", {"graph": graph}, idempotency_key="idem_version")
    client.automations.list_versions("auto/1", limit=5)
    client.automations.publish("auto/1", {"version_id": "ver_1"}, idempotency_key="idem_publish")
    client.automations.pause("auto/1")
    client.automations.resume("auto/1")
    client.automations.rotate_webhook_secret(
        "auto/1", "order/created", idempotency_key="idem_rotate_secret"
    )
    client.automations.create_run(
        "auto/1", {"input": {"order_id": "ord_1"}}, idempotency_key="idem_run"
    )
    client.automations.list_runs("auto/1", status="completed")
    client.automation_runs.retrieve("run/1")
    client.automation_runs.list_steps("run/1", limit=20)
    client.automation_runs.cancel("run/1")
    client.automation_webhooks.invoke(
        "order/created", {"order_id": "ord_1"}, idempotency_key="idem_webhook"
    )
    client.automations.delete("auto/1")

    assert seen[0].headers["idempotency-key"] == "idem_create"
    assert seen[1].url.query.decode() == "limit=10&status=active"
    assert str(seen[2].url) == "https://api.test/v1/automations/auto%2F1"
    assert body(seen[4]) == {"graph": graph}
    assert seen[4].headers["idempotency-key"] == "idem_version"
    assert seen[6].headers["idempotency-key"] == "idem_publish"
    assert not seen[7].content
    assert not seen[8].content
    assert str(seen[9].url).endswith(
        "/automations/auto%2F1/webhook-triggers/order%2Fcreated/rotate-secret"
    )
    assert seen[9].headers["idempotency-key"] == "idem_rotate_secret"
    assert seen[10].headers["idempotency-key"] == "idem_run"
    assert seen[11].url.query.decode() == "status=completed"
    assert str(seen[12].url).endswith("/automation-runs/run%2F1")
    assert seen[13].url.query.decode() == "limit=20"
    assert not seen[14].content
    assert str(seen[15].url).endswith("/automation-webhooks/order%2Fcreated")
    assert seen[15].headers["idempotency-key"] == "idem_webhook"
    assert seen[16].method == "DELETE"
