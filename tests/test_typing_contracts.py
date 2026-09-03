from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_native_pix_and_inbound_media_invalid_shapes_are_rejected(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid_a1_types.py"
    fixture.write_text(
        """\
from tyxter.types import (
    InboundMessageMediaConsumed,
    InboundMessageMediaFailed,
    NativePixOrderDetailsMessagePayload,
    ProviderCredentialSetupSessionCompletedOpenAISttResult,
)

invalid_payment_settings: NativePixOrderDetailsMessagePayload = {
    "type": "order_details",
    "body": {"text": "Review your order"},
    "action": {
        "name": "review_and_pay",
        "parameters": {
            "reference_id": "order_123",
            "type": "physical-goods",
            "payment_type": "br",
            "payment_settings": (
                {
                    "type": "pix_dynamic_code",
                    "pix_dynamic_code": {
                        "code": "one",
                        "merchant_name": "Tyxter Store",
                        "key": "merchant@example.com",
                        "key_type": "EMAIL",
                    },
                },
                {
                    "type": "pix_dynamic_code",
                    "pix_dynamic_code": {
                        "code": "two",
                        "merchant_name": "Tyxter Store",
                        "key": "merchant@example.com",
                        "key_type": "EMAIL",
                    },
                },
            ),
            "currency": "BRL",
            "total_amount": {"value": 12990, "offset": 100},
        },
    },
}

invalid_failed_media: InboundMessageMediaFailed = {
    "asset_id": "mda_123",
    "kind": "audio",
    "mime_type": "audio/ogg",
    "byte_length": 12,
    "filename": None,
    "status": "failed",
}

invalid_consumed_media: InboundMessageMediaConsumed = {
    "asset_id": "mda_123",
    "kind": "audio",
    "mime_type": "audio/ogg",
    "byte_length": 12,
    "filename": None,
    "status": "consumed",
    "failure": {"code": "unexpected", "message": "must be rejected"},
}

invalid_stt_completion: ProviderCredentialSetupSessionCompletedOpenAISttResult = {
    "object": "provider_credential_setup_session",
    "request_id": "pcs_123",
    "project_id": "prj_123",
    "project_slug": "demo",
    "environment_id": "env_123",
    "environment": "production",
    "setup_url": "https://setup.example.test/pcs_123",
    "poll_url": "https://api.example.test/v1/provider-credential-setup-sessions/pcs_123",
    "expires_at": "2026-08-10T12:00:00Z",
    "completed_at": "2026-08-10T11:00:00Z",
    "denied_at": None,
    "created_at": "2026-08-10T10:00:00Z",
    "updated_at": "2026-08-10T11:00:00Z",
    "target": "openai.stt",
    "status": "completed",
    "completed_provider_connection_id": None,
    "completed_tts_provider": "openai",
    "completed_stt_provider": "openai",
}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    source_path = str(PACKAGE_ROOT / "src")
    environment["MYPYPATH"] = (
        source_path
        if not environment.get("MYPYPATH")
        else os.pathsep.join((source_path, environment["MYPYPATH"]))
    )

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", str(fixture)],
        cwd=PACKAGE_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "payment_settings" in output
    assert "failure" in output
    assert "completed_tts_provider" in output


def test_message_media_a2_invalid_shapes_are_rejected(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid_a2_message_media_types.py"
    fixture.write_text(
        """\
from tyxter.types import (
    CreateMessageRequest,
    InboundMessageMediaConsumed,
    InboundUnknownDescriptor,
    InboundUnsupportedDescriptor,
    InstagramMediaMessageInput,
)

invalid_instagram_voice: InstagramMediaMessageInput = {
    "account_id": "ig_123",
    "user_id": "igsid_456",
    "media": {"kind": "audio", "voice": True},
}

none_sender_id: CreateMessageRequest = {
    "channel": "whatsapp",
    "sender": {"type": "whatsapp_phone_number", "id": None},
    "recipient": {"type": "phone_e164", "id": "+15555550100"},
    "message": {"type": "text", "text": {"body": "hello"}},
}

none_recipient_id: CreateMessageRequest = {
    "channel": "whatsapp",
    "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
    "recipient": {"type": "phone_e164", "id": None},
    "message": {"type": "text", "text": {"body": "hello"}},
}

missing_sender: CreateMessageRequest = {
    "channel": "whatsapp",
    "recipient": {"type": "phone_e164", "id": "+15555550100"},
    "message": {"type": "text", "text": {"body": "hello"}},
}

missing_recipient: CreateMessageRequest = {
    "channel": "whatsapp",
    "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
    "message": {"type": "text", "text": {"body": "hello"}},
}

missing_consumed_download: InboundMessageMediaConsumed = {
    "asset_id": "mda_123",
    "kind": "audio",
    "mime_type": "audio/ogg",
    "byte_length": 12,
    "filename": None,
    "status": "consumed",
}

missing_unsupported_fields: InboundUnsupportedDescriptor = {}
missing_unknown_provider_type: InboundUnknownDescriptor = {}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    source_path = str(PACKAGE_ROOT / "src")
    environment["MYPYPATH"] = (
        source_path
        if not environment.get("MYPYPATH")
        else os.pathsep.join((source_path, environment["MYPYPATH"]))
    )

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", str(fixture)],
        cwd=PACKAGE_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert 'Extra key "voice"' in output
    assert 'Missing key "sender"' in output
    assert 'Missing key "recipient"' in output
    assert 'Missing key "download"' in output
    assert "provider_type" in output
    assert "reason" in output
    assert output.count("error:") >= 8


def test_template_parameter_format_invalid_values_are_rejected(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid_a4_template_parameter_formats.py"
    fixture.write_text(
        """\\
from tyxter.types import (
    CreateTemplateRequest,
    DuplicateTemplateRequest,
    TemplateGenerationRequest,
    UpdateTemplateRequest,
)

invalid_create: CreateTemplateRequest = {
    "name": "order_tracking",
    "language": "en_US",
    "category": "utility",
    "parameter_format": "named",
    "components": [],
}

invalid_generate: TemplateGenerationRequest = {
    "description": "Tell a customer their order is ready",
    "language": "en_US",
    "category": "utility",
    "parameter_format": "POSITION",
}

invalid_update: UpdateTemplateRequest = {"parameter_format": "positional"}
invalid_duplicate: DuplicateTemplateRequest = {"parameter_format": "UNSUPPORTED"}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    source_path = str(PACKAGE_ROOT / "src")
    environment["MYPYPATH"] = (
        source_path
        if not environment.get("MYPYPATH")
        else os.pathsep.join((source_path, environment["MYPYPATH"]))
    )

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", str(fixture)],
        cwd=PACKAGE_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "parameter_format" in output
    assert output.count("error:") >= 4


def test_phone_name_review_invalid_shapes_are_rejected(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid_a5_phone_name_review_types.py"
    fixture.write_text(
        """\\
from tyxter.types import (
    PhoneMessagingTier,
    PhoneNumberNameReviewResponse,
    PhoneNumberPendingNameReviewResponse,
)

invalid_tier: PhoneMessagingTier = "tier_3k"

missing_pending_observed_at: PhoneNumberPendingNameReviewResponse = {
    "requested_name": "Tyxter Support",
    "status": "META_FUTURE_PENDING",
}

missing_review_reason: PhoneNumberNameReviewResponse = {
    "requested_name": "Tyxter Support",
    "decision": "META_FUTURE_DECISION",
    "reviewed_at": "2026-09-01T11:00:00Z",
}

invalid_pending_nullable_values: PhoneNumberPendingNameReviewResponse = {
    "requested_name": 123,
    "status": 456,
    "observed_at": "2026-09-01T10:00:00Z",
}

invalid_review_nullable_values: PhoneNumberNameReviewResponse = {
    "requested_name": 123,
    "decision": "META_FUTURE_DECISION",
    "reason": 456,
    "reviewed_at": "2026-09-01T11:00:00Z",
}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    source_path = str(PACKAGE_ROOT / "src")
    environment["MYPYPATH"] = (
        source_path
        if not environment.get("MYPYPATH")
        else os.pathsep.join((source_path, environment["MYPYPATH"]))
    )

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", str(fixture)],
        cwd=PACKAGE_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "tier_3k" in output
    assert "observed_at" in output
    assert "reason" in output
    assert output.count("error:") >= 7


def test_transcription_webhook_cross_variant_fields_are_rejected(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid_a3_transcription_webhook_types.py"
    fixture.write_text(
        """\\
from tyxter.types import (
    MessageMediaTranscribedWebhookTranscript,
    MessageMediaTranscriptionFailedWebhookTranscript,
)

invalid_success: MessageMediaTranscribedWebhookTranscript = {
    "id": "mtr_123",
    "media_asset_id": "mda_123",
    "status": "succeeded",
    "provider": "openai",
    "model": "gpt-4o-transcribe",
    "language": "pt",
    "text": "olá",
    "duration_seconds": 4,
    "completed_at": "2026-08-25T12:00:04Z",
    "error_code": "transcription_failed",
}

invalid_failure: MessageMediaTranscriptionFailedWebhookTranscript = {
    "id": "mtr_456",
    "media_asset_id": "mda_456",
    "status": "failed",
    "error_code": "transcription_failed",
    "error_message": None,
    "language": None,
    "completed_at": "2026-08-25T12:00:04Z",
    "provider": "openai",
}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    source_path = str(PACKAGE_ROOT / "src")
    environment["MYPYPATH"] = (
        source_path
        if not environment.get("MYPYPATH")
        else os.pathsep.join((source_path, environment["MYPYPATH"]))
    )

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", str(fixture)],
        cwd=PACKAGE_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert 'Extra key "error_code"' in output
    assert 'Extra key "provider"' in output
