# Tyxter Python SDK

Python SDK for the Tyxter Messaging API.

The package is currently an in-repo R5a alpha. It starts with a sync
client, public `/v1/*` resource helpers, typed API errors, and webhook
signature verification.

## Install

```bash
pip install -e ".[dev]"
pytest
```

When this package is published, install it with:

```bash
pip install tyxter
```

## Quickstart

```python
from tyxter import Tyxter

client = Tyxter(api_key="tx_sandbox_...", base_url="http://localhost:3001")

message = client.messages.send_text(
    {
        "to": "+15555550100",
        "text": {"body": "Hello from Tyxter Python."},
    },
    idempotency_key="idem_hello_python_001",
)

print(message["id"])
```

## Resources

The R5a surface is intentionally Python-first and synchronous:

```python
client.messages.create({"type": "text", "to": "+15555550100", "text": {"body": "hi"}})
client.messages.get("msg_123")
client.messages.list(limit=20, status="sent")

client.batches.create({"name": "Launch", "recipients": [{"to": "+15555550100"}]})
client.batches.get("batch_123")
client.batches.list(limit=20)

client.contacts.opt_in({"phone": "+15555550100"})
client.contacts.opt_out({"phone": "+15555550100", "reason": "unsubscribe"})
client.contacts.list(limit=20)

client.webhook_endpoints.create(
    {"url": "https://example.com/webhooks/tyxter", "subscribed_events": ["message.sent"]}
)
client.webhook_endpoints.list(limit=20)
```

All write helpers accept `idempotency_key` where the public API supports
idempotent replay. Message, batch, and contact writes also accept `trace_id`
for local debugging and support handoff.

## Errors

API error responses raise `TyxterAPIError` with the Tyxter error envelope
fields attached:

```python
from tyxter import Tyxter, TyxterAPIError

client = Tyxter(api_key="tx_sandbox_...")

try:
    client.messages.create({})
except TyxterAPIError as error:
    print(error.status_code)
    print(error.code)
    print(error.trace_id)
```

Network failures before the API returns a response raise `TyxterConnectionError`.

## Webhooks

Tyxter signs webhook bodies with `HMAC-SHA256(secret, "{timestamp}.{raw_body}")`.
Use the raw request body exactly as received by your framework.

```python
import os

from tyxter import WebhookSignatureVerifier

# signing_secret is the 64-char hex string returned once by
# webhookEndpoints.create / rotate-signing-secret (no prefix).
verifier = WebhookSignatureVerifier(os.environ["TYXTER_WEBHOOK_SECRET"])

is_valid = verifier.verify(
    raw_body=raw_body_bytes,
    headers=request_headers,
)

if not is_valid:
    raise PermissionError("invalid Tyxter webhook signature")
```

Header names are case-insensitive. The default replay tolerance is 300 seconds.

## Local Example

See `examples/sandbox_send_and_verify.py` for a minimal sandbox sender plus
webhook verifier using only public SDK surfaces.

## Broadcast Demo

`examples/broadcast_customer_list.py` sends one approved template to a CSV
customer list through `client.batches.create`.

```bash
python examples/broadcast_customer_list.py \
  --customers examples/customers.csv \
  --from pn_123 \
  --template-name promo_april \
  --template-language en_US \
  --name "April promo" \
  --idempotency-key idem_april_promo_001
```

The CSV must include a `phone` column in E.164 format. Any other non-empty
columns are passed as template variables for that recipient.
