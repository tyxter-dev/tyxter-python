from __future__ import annotations

import os
from collections.abc import Mapping

from tyxter import Tyxter, WebhookSignatureVerifier


def build_client() -> Tyxter:
    return Tyxter(
        api_key=os.environ["TYXTER_API_KEY"],
        base_url=os.environ.get("TYXTER_API_BASE_URL", "https://api.tyxter.com"),
    )


def send_sandbox_message(
    client: Tyxter,
    *,
    to: str,
    idempotency_key: str = "idem_python_quickstart_001",
) -> dict[str, object]:
    return client.messages.send_text(
        {
            "to": to,
            "text": {"body": "Hello from the Tyxter Python SDK."},
        },
        idempotency_key=idempotency_key,
    )


def verify_tyxter_webhook(
    *,
    raw_body: bytes,
    headers: Mapping[str, str],
    signing_secret: str,
    now: int | None = None,
) -> bool:
    return WebhookSignatureVerifier(signing_secret).verify(
        raw_body=raw_body,
        headers=headers,
        now=now,
    )


def main() -> None:
    client = build_client()
    message = send_sandbox_message(
        client,
        to=os.environ.get("TYXTER_TO", "+15555550100"),
    )
    print(message["id"])


if __name__ == "__main__":
    main()
