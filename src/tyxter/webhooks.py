from __future__ import annotations

import hmac
import time
from collections.abc import Mapping
from hashlib import sha256

WEBHOOK_ID_HEADER = "tyxter-webhook-id"
WEBHOOK_TIMESTAMP_HEADER = "tyxter-webhook-timestamp"
WEBHOOK_SIGNATURE_HEADER = "tyxter-webhook-signature"
DEFAULT_WEBHOOK_TOLERANCE_SECONDS = 300

RawBody = str | bytes


def sign_webhook(secret: str, timestamp: str, raw_body: RawBody) -> str:
    body = _coerce_body(raw_body)
    payload = timestamp.encode("utf-8") + b"." + body
    return hmac.new(secret.encode("utf-8"), payload, sha256).hexdigest()


def verify_webhook_signature(
    *,
    secret: str,
    timestamp: str,
    raw_body: RawBody,
    signature: str,
    tolerance_seconds: int = DEFAULT_WEBHOOK_TOLERANCE_SECONDS,
    now: int | None = None,
) -> bool:
    try:
        timestamp_seconds = int(timestamp)
    except ValueError:
        return False

    current_seconds = int(time.time()) if now is None else now
    if abs(current_seconds - timestamp_seconds) > tolerance_seconds:
        return False

    expected = sign_webhook(secret, timestamp, raw_body)
    return hmac.compare_digest(expected, signature)


class WebhookSignatureVerifier:
    def __init__(
        self,
        secret: str,
        *,
        tolerance_seconds: int = DEFAULT_WEBHOOK_TOLERANCE_SECONDS,
    ) -> None:
        if not secret:
            raise ValueError("secret is required")
        self.secret = secret
        self.tolerance_seconds = tolerance_seconds

    def verify(
        self,
        *,
        raw_body: RawBody,
        headers: Mapping[str, str],
        now: int | None = None,
    ) -> bool:
        normalized = {key.lower(): value for key, value in headers.items()}
        timestamp = normalized.get(WEBHOOK_TIMESTAMP_HEADER)
        signature = normalized.get(WEBHOOK_SIGNATURE_HEADER)
        if timestamp is None or signature is None:
            return False
        return verify_webhook_signature(
            secret=self.secret,
            timestamp=timestamp,
            raw_body=raw_body,
            signature=signature,
            tolerance_seconds=self.tolerance_seconds,
            now=now,
        )


def _coerce_body(raw_body: RawBody) -> bytes:
    if isinstance(raw_body, bytes):
        return raw_body
    return raw_body.encode("utf-8")
