from __future__ import annotations

import httpx
import pytest

from tyxter import Tyxter, TyxterAPIError, TyxterConnectionError


def test_request_sends_auth_json_headers_and_idempotency_key() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"id": "msg_123"})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test/",
        transport=httpx.MockTransport(handler),
    )

    body = client._request(
        "POST",
        "/v1/messages",
        json={"to": "+15555550100"},
        idempotency_key="idem_123",
    )

    assert body == {"id": "msg_123"}
    assert len(seen) == 1
    request = seen[0]
    assert str(request.url) == "https://api.test/v1/messages"
    assert request.headers["authorization"] == "Bearer tx_sandbox_test"
    assert request.headers["user-agent"] == "tyxter-python/0.1.0a0"
    assert request.headers["accept"] == "application/json"
    assert request.headers["content-type"] == "application/json"
    assert request.headers["idempotency-key"] == "idem_123"
    assert request.read() == b'{"to":"+15555550100"}'


def test_get_request_uses_query_params_without_content_type() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": []})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    body = client._request("GET", "/v1/messages", params={"limit": 10, "cursor": "cur_123"})

    assert body == {"data": []}
    request = seen[0]
    assert str(request.url) == "https://api.test/v1/messages?limit=10&cursor=cur_123"
    assert "content-type" not in request.headers


def test_timeout_configuration_is_applied_to_owned_http_client() -> None:
    client = Tyxter(api_key="tx_sandbox_test", timeout=12.5)

    assert client.timeout == 12.5
    assert client._client.timeout.connect == 12.5
    client.close()


def test_raises_typed_api_error_from_tyxter_error_envelope() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={
                "error": {
                    "type": "validation_error",
                    "code": "invalid_message_request",
                    "message": "to is required.",
                    "param": "to",
                    "request_id": "req_123",
                    "trace_id": "trc_123",
                    "retry_after_ms": 250,
                }
            },
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TyxterAPIError) as exc_info:
        client._request("POST", "/v1/messages", json={})

    error = exc_info.value
    assert str(error) == "to is required."
    assert error.status_code == 422
    assert error.type == "validation_error"
    assert error.code == "invalid_message_request"
    assert error.param == "to"
    assert error.request_id == "req_123"
    assert error.trace_id == "trc_123"
    assert error.retry_after_ms == 250
    assert error.body == {
        "error": {
            "type": "validation_error",
            "code": "invalid_message_request",
            "message": "to is required.",
            "param": "to",
            "request_id": "req_123",
            "trace_id": "trc_123",
            "retry_after_ms": 250,
        }
    }


def test_raises_fallback_api_error_for_non_json_error_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="temporarily unavailable")

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TyxterAPIError) as exc_info:
        client._request("GET", "/v1/messages")

    error = exc_info.value
    assert error.status_code == 503
    assert error.type == "api_error"
    assert error.code == "http_503"
    assert error.body == "temporarily unavailable"


def test_wraps_network_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TyxterConnectionError) as exc_info:
        client._request("GET", "/v1/messages")

    assert "connection refused" in str(exc_info.value)
