from __future__ import annotations

import json

import pytest

from tyxter import WebhookSignatureVerifier, sign_webhook, verify_webhook_signature

SECRET = "wh_secret_abcdef"
TIMESTAMP = "1714123456"
BODY = '{"type":"message.sent","id":"msg_1"}'
SIGNATURE = "f0754d8d0c9d40377677808b0a73c05ee2e52128e6b0060bd7a5c888650c2921"
TRANSCRIBED_WEBHOOK_BODY = (
    '{"id":"evt_transcribed","type":"message.media_transcribed",'
    '"created_at":"2026-08-25T12:00:00Z","environment":"sandbox",'
    '"trace_id":"trc_transcribed","data":{"message_id":"msg_123","status":"delivered",'
    '"channel":"whatsapp","sender":{"type":"phone_e164","id":"+15555550100"},'
    '"recipient":{"type":"whatsapp_phone_number","id":"pn_123"},'
    '"provider_message_id":"wamid_123","metadata":null,"transcript":{"id":"mtr_123",'
    '"media_asset_id":"mda_123","status":"succeeded","provider":"openai",'
    '"model":"gpt-4o-transcribe","language":"pt","text":"olá",'
    '"duration_seconds":4,"completed_at":"2026-08-25T12:00:04Z"}}}'
)
TRANSCRIPTION_FAILED_WEBHOOK_BODY = (
    '{"id":"evt_failed","type":"message.media_transcription_failed",'
    '"created_at":"2026-08-25T12:00:00Z","occurred_at":"2026-08-25T12:00:04Z",'
    '"environment":"production","trace_id":"trc_failed","data":{"message_id":"msg_456",'
    '"status":"failed","channel":"instagram","sender":{"type":"instagram_user","id":"ig_1"},'
    '"recipient":{"type":"instagram_account","id":"ig_business_1"},'
    '"provider_message_id":null,"metadata":null,"transcript":{"id":"mtr_456",'
    '"media_asset_id":"mda_456","status":"failed","error_code":"transcription_failed",'
    '"error_message":"Provider rejected the media.","language":null,'
    '"completed_at":"2026-08-25T12:00:04Z"}}}'
)
POLICY_WARNING_WEBHOOK_BODY = (
    '{"id":"evt_policy_warning","type":"provider_connection.policy_warning",'
    '"created_at":"2026-09-01T10:00:00Z","environment":"sandbox",'
    '"trace_id":"trc_policy_warning","data":{"provider_connection_id":"pc_123",'
    '"provider":"meta","display_name":"Tyxter Support",'
    '"violation_type":"META_FUTURE_VIOLATION","observed_at":"2026-09-01T10:00:00Z"}}'
)
DISABLE_SCHEDULED_WEBHOOK_BODY = (
    '{"id":"evt_disable_scheduled","type":"provider_connection.disable_scheduled",'
    '"created_at":"2026-09-01T10:00:00Z","environment":"production",'
    '"trace_id":"trc_disable_scheduled","data":{"provider_connection_id":"pc_123",'
    '"provider":"meta","display_name":"Tyxter Support",'
    '"waba_ban_date":null,"observed_at":"2026-09-01T10:00:00Z"}}'
)


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


@pytest.mark.parametrize(
    ("raw_body", "event_type", "transcript_status"),
    [
        (TRANSCRIBED_WEBHOOK_BODY, "message.media_transcribed", "succeeded"),
        (
            TRANSCRIPTION_FAILED_WEBHOOK_BODY,
            "message.media_transcription_failed",
            "failed",
        ),
    ],
)
def test_transcription_webhook_json_fixtures_verify_as_opaque_raw_bodies(
    raw_body: str,
    event_type: str,
    transcript_status: str,
) -> None:
    signature = sign_webhook(SECRET, TIMESTAMP, raw_body)
    verifier = WebhookSignatureVerifier(SECRET)

    parsed = json.loads(raw_body)
    assert parsed["type"] == event_type
    assert parsed["data"]["transcript"]["status"] == transcript_status
    assert verify_webhook_signature(
        secret=SECRET,
        timestamp=TIMESTAMP,
        raw_body=raw_body,
        signature=signature,
        now=int(TIMESTAMP),
    )
    assert verifier.verify(
        raw_body=raw_body,
        headers={
            "tyxter-webhook-timestamp": TIMESTAMP,
            "tyxter-webhook-signature": signature,
        },
        now=int(TIMESTAMP),
    )
    assert not verifier.verify(
        raw_body=f"{raw_body} ",
        headers={
            "tyxter-webhook-timestamp": TIMESTAMP,
            "tyxter-webhook-signature": signature,
        },
        now=int(TIMESTAMP),
    )


@pytest.mark.parametrize(
    ("raw_body", "event_type"),
    [
        (POLICY_WARNING_WEBHOOK_BODY, "provider_connection.policy_warning"),
        (DISABLE_SCHEDULED_WEBHOOK_BODY, "provider_connection.disable_scheduled"),
    ],
)
def test_provider_connection_webhook_json_fixtures_verify_as_opaque_raw_bodies(
    raw_body: str,
    event_type: str,
) -> None:
    signature = sign_webhook(SECRET, TIMESTAMP, raw_body)
    verifier = WebhookSignatureVerifier(SECRET)

    parsed = json.loads(raw_body)
    assert parsed["type"] == event_type
    assert parsed["data"]["provider"] == "meta"
    assert verifier.verify(
        raw_body=raw_body,
        headers={
            "tyxter-webhook-timestamp": TIMESTAMP,
            "tyxter-webhook-signature": signature,
        },
        now=int(TIMESTAMP),
    )
    assert not verifier.verify(
        raw_body=f"{raw_body} ",
        headers={
            "tyxter-webhook-timestamp": TIMESTAMP,
            "tyxter-webhook-signature": signature,
        },
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
