from __future__ import annotations

import json
from typing import cast

import httpx

from tyxter import Tyxter


def test_projects_resource_covers_paths_queries_headers_and_response_shapes() -> None:
    seen: list[httpx.Request] = []
    project: dict[str, object] = {
        "id": "prj_1",
        "object": "project",
        "name": "Demo",
        "slug": "demo",
        "default_language": "pt_BR",
        "profile": {
            "about": None,
            "description": None,
            "address": None,
            "email": None,
            "websites": [],
            "vertical": None,
            "profile_image_url": None,
            "profile_image_mime_type": None,
            "profile_image_size_bytes": None,
            "profile_image_uploaded_at": None,
            "meta_sync": {
                "status": "not_synced",
                "synced_at": None,
                "phone_number_id": None,
                "profile_picture_url": None,
                "error_code": None,
                "error_message": None,
            },
        },
        "archived_at": None,
        "created_at": "2026-09-03T00:00:00Z",
        "updated_at": "2026-09-03T00:00:00Z",
        "environments": [
            {
                "id": "env_1",
                "object": "environment",
                "kind": "sandbox",
                "name": "Sandbox",
                "throughput_tier": "starter",
                "created_at": "2026-09-03T00:00:00Z",
                "updated_at": "2026-09-03T00:00:00Z",
            }
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/v1/projects" and request.method == "GET":
            return httpx.Response(
                200,
                json={"object": "list", "data": [project], "has_more": False, "next_cursor": None},
            )
        return httpx.Response(200, json=project)

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    created = client.projects.create(
        {"name": "Demo", "slug": "demo"}, idempotency_key="idem_project"
    )
    listed = client.projects.list(limit=3, starting_after="prj_0")
    retrieved = client.projects.retrieve("prj/1")

    assert created["environments"][0]["kind"] == "sandbox"
    assert listed["data"][0]["profile"]["meta_sync"]["status"] == "not_synced"
    assert retrieved["default_language"] == "pt_BR"
    assert cast(dict[str, object], json.loads(seen[0].read())) == {"name": "Demo", "slug": "demo"}
    assert seen[0].headers["idempotency-key"] == "idem_project"
    assert str(seen[1].url) == "https://api.test/v1/projects?limit=3&starting_after=prj_0"
    assert str(seen[2].url) == "https://api.test/v1/projects/prj%2F1"
    assert all("idempotency-key" not in request.headers for request in seen[1:])
    assert all("tyxter-trace-id" not in request.headers for request in seen)
