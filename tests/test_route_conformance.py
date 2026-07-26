from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
MANIFEST_PATH = (
    REPO_ROOT
    / "packages"
    / "contracts"
    / "api"
    / "tests"
    / "snapshots"
    / "public-api-launch-endpoints.json"
)
QUERY_PARAMS_PATH = MANIFEST_PATH.with_name("public-api-query-params.json")

# A resource moves out of this ledger only when every one of its manifest
# routes has a typed SDK method and route-level tests. A newly introduced
# manifest resource fails the classification test until it is reviewed.
DEFERRED_RESOURCES: dict[str, str] = {}

SUPPORTED_RESOURCES = {
    "account",
    "agent_api_key_device_authorizations",
    "api_keys",
    "ai_agents",
    "agentic_payments",
    "automation_runs",
    "automation_webhooks",
    "automations",
    "audiences",
    "batches",
    "billing",
    "contacts",
    "data_retention",
    "feedback",
    "fiscal",
    "flows",
    "llm",
    "llm_routes",
    "messages",
    "media",
    "payments",
    "phone_numbers",
    "provider_connections",
    "rate_cards",
    "sandbox",
    "templates",
    "usage",
    "webhook_endpoints",
    "webhook_events",
}

REVIEWED_ROUTE_EXEMPTIONS = {
    "PUT /v1/media/blobs/:param",
    "GET /v1/media/blobs/:param",
}


@dataclass(frozen=True)
class CoveredRoute:
    method: str
    path: str
    source: str
    function: str
    idempotency_key: bool
    trace_id_header: bool
    # Keys of the literal `params={...}` dict passed to _request, None when the
    # call sends no query params. A non-literal params expression is recorded as
    # {"<dynamic>"} so the query-param gate flags it instead of skipping it.
    query_params: frozenset[str] | None

    @property
    def key(self) -> str:
        return route_key(self.method, self.path)


def route_key(method: str, path: str) -> str:
    normalized = re.sub(r":[A-Za-z0-9_]+", ":param", path)
    return f"{method.upper()} {normalized}"


def load_manifest() -> list[dict[str, Any]]:
    return cast(
        list[dict[str, Any]],
        json.loads(MANIFEST_PATH.read_text(encoding="utf-8")),
    )


def load_query_params_snapshot() -> dict[str, list[str]]:
    return cast(
        dict[str, list[str]],
        json.loads(QUERY_PARAMS_PATH.read_text(encoding="utf-8")),
    )


def _query_param_keys(call: ast.Call) -> frozenset[str] | None:
    for keyword in call.keywords:
        if keyword.arg != "params":
            continue
        value = keyword.value
        if isinstance(value, ast.Dict):
            keys: list[str] = []
            for key in value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.append(key.value)
                else:
                    return frozenset({"<dynamic>"})
            return frozenset(keys)
        return frozenset({"<dynamic>"})
    return None


def _string_expression(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append(":param")
            else:
                return None
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _string_expression(node.left)
        right = _string_expression(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def extract_routes() -> list[CoveredRoute]:
    covered: list[CoveredRoute] = []
    resources_dir = PACKAGE_ROOT / "src" / "tyxter" / "resources"
    for source_path in sorted(resources_dir.glob("[!_]*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            parameter_names = {
                argument.arg for argument in (*node.args.args, *node.args.kwonlyargs)
            }
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                if not (
                    isinstance(child.func, ast.Attribute)
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id == "self"
                    and child.func.attr == "_request"
                    and len(child.args) >= 2
                ):
                    continue
                method = _string_expression(child.args[0])
                path = _string_expression(child.args[1])
                if method is None or path is None or not path.startswith("/v1/"):
                    continue
                forwarded = {
                    keyword.arg
                    for keyword in child.keywords
                    if keyword.arg is not None
                    and isinstance(keyword.value, ast.Name)
                    and keyword.value.id == keyword.arg
                }
                covered.append(
                    CoveredRoute(
                        method=method,
                        path=path,
                        source=source_path.name,
                        function=node.name,
                        idempotency_key=(
                            "idempotency_key" in parameter_names and "idempotency_key" in forwarded
                        ),
                        trace_id_header=("trace_id" in parameter_names and "trace_id" in forwarded),
                        query_params=_query_param_keys(child),
                    )
                )
    return covered


@pytest.fixture(scope="module")
def manifest() -> list[dict[str, Any]]:
    return load_manifest()


@pytest.fixture(scope="module")
def covered() -> list[CoveredRoute]:
    return extract_routes()


def test_every_manifest_resource_is_supported_or_reviewed(
    manifest: list[dict[str, Any]],
) -> None:
    manifest_resources = {str(endpoint["resource"]) for endpoint in manifest}
    classified = SUPPORTED_RESOURCES | set(DEFERRED_RESOURCES)
    assert classified == manifest_resources


def test_supported_resources_cover_every_manifest_route(
    manifest: list[dict[str, Any]], covered: list[CoveredRoute]
) -> None:
    manifest_keys = {
        route_key(str(endpoint["method"]), str(endpoint["path"]))
        for endpoint in manifest
        if endpoint["resource"] in SUPPORTED_RESOURCES
    }
    covered_keys = {route.key for route in covered}
    assert covered_keys | REVIEWED_ROUTE_EXEMPTIONS == manifest_keys
    assert covered_keys.isdisjoint(REVIEWED_ROUTE_EXEMPTIONS)


def test_python_sdk_has_no_phantom_or_duplicate_routes(
    manifest: list[dict[str, Any]], covered: list[CoveredRoute]
) -> None:
    manifest_keys = {
        route_key(str(endpoint["method"]), str(endpoint["path"])) for endpoint in manifest
    }
    covered_keys = [route.key for route in covered]
    assert set(covered_keys) <= manifest_keys
    assert REVIEWED_ROUTE_EXEMPTIONS <= manifest_keys
    duplicates = sorted(key for key in set(covered_keys) if covered_keys.count(key) > 1)
    assert duplicates == []


def test_query_params_match_the_canonical_contracts(
    manifest: list[dict[str, Any]], covered: list[CoveredRoute]
) -> None:
    """Every SDK method's query surface equals its manifest query schema.

    The schema param names come from the Zod-derived snapshot
    public-api-query-params.json (locked by contracts-api's
    query-params.test.ts), so a query param added to a contract schema fails
    here until the SDK method exposes it — the silent-drift class of #425
    (messages.list() missing `direction`/`include`).
    """
    snapshot = load_query_params_snapshot()
    by_key = {
        route_key(str(endpoint["method"]), str(endpoint["path"])): endpoint for endpoint in manifest
    }
    mismatches: list[str] = []
    for route in covered:
        endpoint = by_key[route.key]
        schema_name = cast(str | None, endpoint["query_schema"])
        if schema_name is not None and schema_name not in snapshot:
            mismatches.append(
                f"{route.key}: query_schema {schema_name} missing from "
                f"public-api-query-params.json — regenerate the snapshot"
            )
            continue
        expected = set(snapshot[schema_name]) if schema_name is not None else set()
        actual = set(route.query_params or frozenset())
        if actual != expected:
            missing = sorted(expected - actual)
            phantom = sorted(actual - expected)
            mismatches.append(
                f"{route.key} ({route.source}:{route.function}) missing={missing} phantom={phantom}"
            )
    assert mismatches == []


def test_supported_headers_match_the_canonical_manifest(
    manifest: list[dict[str, Any]], covered: list[CoveredRoute]
) -> None:
    by_key = {
        route_key(str(endpoint["method"]), str(endpoint["path"])): endpoint for endpoint in manifest
    }
    mismatches: list[str] = []
    for route in covered:
        endpoint = by_key[route.key]
        expected_idempotency = endpoint["idempotency_key"] == "supported"
        expected_trace = endpoint["trace_id_header"] == "supported"
        if route.idempotency_key != expected_idempotency:
            mismatches.append(
                f"{route.key} idempotency: SDK={route.idempotency_key} "
                f"manifest={expected_idempotency} ({route.source}:{route.function})"
            )
        if route.trace_id_header != expected_trace:
            mismatches.append(
                f"{route.key} trace: SDK={route.trace_id_header} "
                f"manifest={expected_trace} ({route.source}:{route.function})"
            )
    assert mismatches == []
