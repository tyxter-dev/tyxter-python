from __future__ import annotations

import json
from typing import cast

import httpx
import pytest

from tyxter import Tyxter, TyxterMediaUploadError


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def test_media_direct_operations_match_routes_queries_and_trace_headers() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.media.create_upload(
        {"kind": "image", "mime_type": "image/png", "byte_length": 3},
        idempotency_key="idem_create",
        trace_id="trc_media",
    )
    client.media.complete_upload("asset/1", idempotency_key="idem_complete", trace_id="trc_media")
    client.media.list(
        limit=10,
        lifecycle="library",
        status="ready",
        kind="image",
        trace_id="trc_media",
    )
    client.media.storage_usage(trace_id="trc_media")
    client.media.retrieve("asset/1", trace_id="trc_media")
    client.media.delete("asset/1", trace_id="trc_media")

    assert body(seen[0]) == {"kind": "image", "mime_type": "image/png", "byte_length": 3}
    assert seen[0].headers["idempotency-key"] == "idem_create"
    assert str(seen[1].url) == "https://api.test/v1/media/uploads/asset%2F1/complete"
    assert not seen[1].content
    assert seen[1].headers["idempotency-key"] == "idem_complete"
    assert seen[2].url.query.decode() == ("limit=10&lifecycle=library&status=ready&kind=image")
    assert seen[3].url.path == "/v1/media/storage-usage"
    assert str(seen[4].url) == "https://api.test/v1/media/asset%2F1"
    assert str(seen[5].url) == "https://api.test/v1/media/asset%2F1"
    assert seen[5].method == "DELETE"
    for request in seen:
        assert request.headers["tyxter-trace-id"] == "trc_media"


def test_media_upload_uses_returned_capability_url_without_bearer_auth() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.method == "POST" and request.url.path == "/v1/media/uploads":
            return httpx.Response(
                201,
                json={
                    "id": "asset_1",
                    "object": "media_upload",
                    "upload_url": "https://upload.test/v1/media/blobs/capability-token",
                    "upload_method": "PUT",
                    "upload_headers": {"content-type": "image/png", "x-upload": "one"},
                    "expires_at": "2026-07-14T12:00:00Z",
                },
            )
        if request.method == "PUT":
            return httpx.Response(200)
        return httpx.Response(200, json={"id": "asset_1", "object": "media_asset"})

    client = Tyxter(
        api_key="tx_sandbox_secret",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.media.upload(
        {
            "kind": "image",
            "filename": "one.png",
            "mime_type": "image/png",
            "byte_length": 3,
            "body": b"png",
        },
        create_idempotency_key="idem_create",
        complete_idempotency_key="idem_complete",
        trace_id="trc_upload",
    )

    assert [(request.method, str(request.url)) for request in seen] == [
        ("POST", "https://api.test/v1/media/uploads"),
        ("PUT", "https://upload.test/v1/media/blobs/capability-token"),
        ("POST", "https://api.test/v1/media/uploads/asset_1/complete"),
    ]
    assert seen[1].content == b"png"
    assert seen[1].headers["content-type"] == "image/png"
    assert seen[1].headers["x-upload"] == "one"
    assert "authorization" not in seen[1].headers
    assert seen[0].headers["authorization"] == "Bearer tx_sandbox_secret"
    assert seen[2].headers["authorization"] == "Bearer tx_sandbox_secret"


def test_media_upload_raises_typed_error_before_complete_on_capability_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.test":
            return httpx.Response(
                201,
                json={
                    "id": "asset_1",
                    "object": "media_upload",
                    "upload_url": "https://upload.test/v1/media/blobs/token",
                    "upload_method": "PUT",
                    "upload_headers": {},
                    "expires_at": "2026-07-14T12:00:00Z",
                },
            )
        return httpx.Response(413)

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TyxterMediaUploadError) as exc_info:
        client.media.upload(
            {
                "kind": "image",
                "mime_type": "image/png",
                "byte_length": 3,
                "body": b"png",
            }
        )

    assert exc_info.value.status_code == 413


def test_usage_resources_emit_canonical_query_names() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.usage.retrieve(
        period_start="2026-07-01T00:00:00Z",
        period_end="2026-08-01T00:00:00Z",
        environment="sandbox",
        group_by="template_id",
    )
    client.usage.list_records(
        limit=25,
        starting_after="ur_1",
        environment="sandbox",
        meter_id="msg.transport",
        recorded_after="2026-07-01T00:00:00Z",
        recorded_before="2026-08-01T00:00:00Z",
    )

    assert seen[0].url.query.decode() == (
        "period_start=2026-07-01T00%3A00%3A00Z&period_end=2026-08-01T00%3A00%3A00Z"
        "&environment=sandbox&group_by=template_id"
    )
    assert seen[1].url.path == "/v1/usage/records"
    assert "meter_id=msg.transport" in seen[1].url.query.decode()


def test_payments_resource_covers_create_list_retrieve_and_approval() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.payments.create(
        {"amount_brl_centavos": 12990, "external_reference": "ord_123"},
        idempotency_key="idem_pay",
        trace_id="trc_pay",
    )
    client.payments.list(limit=10, status="paid")
    client.payments.retrieve("pay/1")
    client.payments.request_approval(
        "pay/1",
        {"note": "retry"},
        idempotency_key="idem_approval",
        trace_id="trc_approval",
    )

    assert body(seen[0]) == {"amount_brl_centavos": 12990, "external_reference": "ord_123"}
    assert seen[0].headers["idempotency-key"] == "idem_pay"
    assert seen[0].headers["tyxter-trace-id"] == "trc_pay"
    assert str(seen[1].url) == "https://api.test/v1/payments?limit=10&status=paid"
    assert str(seen[2].url) == "https://api.test/v1/payments/pay%2F1"
    assert str(seen[3].url) == "https://api.test/v1/payments/pay%2F1/request-approval"
    assert body(seen[3]) == {"note": "retry"}
    assert seen[3].headers["idempotency-key"] == "idem_approval"
    assert seen[3].headers["tyxter-trace-id"] == "trc_approval"
