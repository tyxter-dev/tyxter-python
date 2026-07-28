from __future__ import annotations

from typing import get_args

import httpx
import pytest

from tyxter import Tyxter, TyxterAPIError, TyxterConnectionError
from tyxter.errors import _SUPPORTED_ERROR_TYPES
from tyxter.types import TyxterErrorType


def test_runtime_error_types_match_typed_contract() -> None:
    assert set(get_args(TyxterErrorType)) == _SUPPORTED_ERROR_TYPES


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


def test_returns_none_for_empty_or_no_content_responses() -> None:
    responses = iter(
        [
            httpx.Response(204),
            httpx.Response(200, content=b""),
        ]
    )

    def handler(_: httpx.Request) -> httpx.Response:
        return next(responses)

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    assert client._request("DELETE", "/v1/webhook-events/listen-sessions/lsn_1") is None
    assert client._request("GET", "/v1/account") is None


def test_invalid_json_success_response_falls_back_to_text() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"not-json",
            headers={"content-type": "application/json"},
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    assert client._request("GET", "/v1/account") == "not-json"


def test_injected_http_client_uses_tyxter_base_url_and_remains_caller_owned() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"object": "account"})

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test/root",
        http_client=http_client,
    )

    client._request("GET", "/v1/account")
    client.close()

    assert str(seen[0].url) == "https://api.test/root/v1/account"
    assert not http_client.is_closed
    http_client.close()


def test_rejects_transport_when_http_client_is_injected() -> None:
    http_client = httpx.Client()
    try:
        with pytest.raises(ValueError, match="transport cannot be combined with http_client"):
            Tyxter(
                api_key="tx_sandbox_test",
                http_client=http_client,
                transport=httpx.MockTransport(lambda _: httpx.Response(200)),
            )
    finally:
        http_client.close()


def test_client_repr_does_not_expose_api_key() -> None:
    api_key = "tx_sandbox_do_not_log_this"
    client = Tyxter(api_key=api_key)

    assert api_key not in repr(client)
    client.close()


def test_parses_optional_feedback_pointer() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            json={
                "error": {
                    "type": "internal_error",
                    "code": "internal_error",
                    "message": "unexpected failure",
                    "feedback": {"endpoint": "/v1/feedback", "method": "POST"},
                }
            },
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(TyxterAPIError) as exc_info:
        client._request("GET", "/v1/account")

    assert exc_info.value.feedback == {"endpoint": "/v1/feedback", "method": "POST"}
