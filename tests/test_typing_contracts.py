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
