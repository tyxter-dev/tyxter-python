from __future__ import annotations

from tyxter import WebhookSignatureVerifier, sign_webhook, verify_webhook_signature

SECRET = "wh_secret_abcdef"
TIMESTAMP = "1714123456"
BODY = '{"type":"message.sent","id":"msg_1"}'
SIGNATURE = "f0754d8d0c9d40377677808b0a73c05ee2e52128e6b0060bd7a5c888650c2921"


def test_sign_webhook_matches_platform_crypto_vector() -> None:
    assert sign_webhook(SECRET, TIMESTAMP, BODY) == SIGNATURE


def test_verify_webhook_signature_accepts_valid_signature() -> None:
    assert verify_webhook_signature(
        secret=SECRET,
        timestamp=TIMESTAMP,
        raw_body=BODY,
        signature=SIGNATURE,
        now=int(TIMESTAMP),
    )


def test_verify_webhook_signature_accepts_bytes_body() -> None:
    assert verify_webhook_signature(
        secret=SECRET,
        timestamp=TIMESTAMP,
        raw_body=BODY.encode("utf-8"),
        signature=SIGNATURE,
        now=int(TIMESTAMP),
    )


def test_verify_webhook_signature_rejects_tampering() -> None:
    assert not verify_webhook_signature(
        secret=SECRET,
        timestamp=TIMESTAMP,
        raw_body=f"{BODY}!",
        signature=SIGNATURE,
        now=int(TIMESTAMP),
    )


def test_verify_webhook_signature_rejects_stale_timestamp() -> None:
    assert not verify_webhook_signature(
        secret=SECRET,
        timestamp=TIMESTAMP,
        raw_body=BODY,
        signature=SIGNATURE,
        now=int(TIMESTAMP) + 301,
    )


def test_verify_webhook_signature_rejects_malformed_timestamp() -> None:
    assert not verify_webhook_signature(
        secret=SECRET,
        timestamp="not-a-timestamp",
        raw_body=BODY,
        signature=SIGNATURE,
        now=int(TIMESTAMP),
    )


def test_verify_webhook_signature_rejects_wrong_signature_length_without_throwing() -> None:
    assert not verify_webhook_signature(
        secret=SECRET,
        timestamp=TIMESTAMP,
        raw_body=BODY,
        signature="too-short",
        now=int(TIMESTAMP),
    )


def test_header_verifier_uses_case_insensitive_tyxter_headers() -> None:
    verifier = WebhookSignatureVerifier(SECRET)

    assert verifier.verify(
        raw_body=BODY,
        headers={
            "Tyxter-Webhook-Id": "evt_123",
            "Tyxter-Webhook-Timestamp": TIMESTAMP,
            "Tyxter-Webhook-Signature": SIGNATURE,
        },
        now=int(TIMESTAMP),
    )


def test_header_verifier_rejects_missing_headers() -> None:
    verifier = WebhookSignatureVerifier(SECRET)

    assert not verifier.verify(
        raw_body=BODY,
        headers={"tyxter-webhook-timestamp": TIMESTAMP},
        now=int(TIMESTAMP),
    )


def test_header_verifier_requires_secret() -> None:
    try:
        WebhookSignatureVerifier("")
    except ValueError as exc:
        assert str(exc) == "secret is required"
    else:
        raise AssertionError("expected ValueError")
