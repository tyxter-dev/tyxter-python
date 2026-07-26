# Tyxter Python SDK

Typed, synchronous Python client for the Tyxter Messaging API. The package uses
`httpx`, supports Python 3.10–3.13, and covers every SDK-callable route in the
public launch manifest.

The SDK is alpha software. Additive response fields are compatible and are
tolerated at runtime. Removing or renaming a public method, field, or stable
`error.code` requires a deprecation cycle.

## Install

```bash
pip install tyxter
```

For repository development:

```bash
cd sdks/python
pip install -e ".[dev]"
pytest
```

## First message

```python
import os

from tyxter import Tyxter

with Tyxter(api_key=os.environ["TYXTER_API_KEY"]) as client:
    account = client.account.retrieve()
    sender_id = client.sandbox.quickstart()["sender"]["default_sender_id"]
    if sender_id is None:
        raise RuntimeError("sandbox sender is not configured")

    # A customer inbound opens WhatsApp's 24-hour free-form service window.
    client.sandbox.inbound_messages.create(
        {
            "from": "+15555550100",
            "to": sender_id,
            "type": "text",
            "text": {"body": "ping"},
        },
        idempotency_key="idem_python_open_window_001",
    )
    message = client.whatsapp.send_text(
        {
            "from": sender_id,
            "to": "+15555550100",
            "body": "Hello from Tyxter Python.",
        },
        idempotency_key="idem_python_first_message_001",
    )
    detail = client.messages.retrieve(message["id"])

print(account["environment"]["kind"], detail["status"], message["trace_id"])
```

Set `base_url="http://localhost:3001"` when using the local stack.

The complete deterministic example at
`examples/sandbox_send_and_verify.py` sends a sandbox message, retrieves it,
polls the public webhook-listen API, and verifies the returned raw-body
signature preview without using dashboard or internal routes.

```bash
TYXTER_API_KEY=tx_sandbox_... \
TYXTER_WEBHOOK_SECRET=... \
python examples/sandbox_send_and_verify.py
```

## Resources

The client exposes snake-case resource namespaces:

- `account`, `api_keys`, `ai_agents`, `agentic_payments`, and `audiences`
- `automations`, `automation_runs`, and `automation_webhooks`
- `batches`, `billing`, `contacts`, `data_retention`, `feedback`, `fiscal`,
  and `flows`
- `llm`, `llm_routes`, `media`, `messages`, and `payments`
- `phone_numbers`, `provider_connections`, and
  `provider_credential_setup_sessions`
- `rate_cards`, `sandbox`, `templates`, `usage`, `webhook_endpoints`, and
  `webhook_events`
- channel-native conveniences: `whatsapp`, `instagram`, and
  `whatsapp_channels`

Request and response dictionaries are `TypedDict` contracts exported from
`tyxter.types`. Write methods expose `idempotency_key` and `trace_id` only where
the canonical endpoint manifest supports those headers.

## Pagination

List methods return cursor pages. Continue with `next_cursor` only when
`has_more` is true:

```python
cursor = None
while True:
    page = client.messages.list(limit=100, starting_after=cursor)
    for message in page["data"]:
        print(message["id"], message["status"])
    if not page["has_more"]:
        break
    cursor = page["next_cursor"]
```

## Idempotency and errors

Tyxter does not implicitly retry writes. Reuse one idempotency key for retries
of the same logical operation and choose your retry policy from the stable error
fields:

```python
from tyxter import TyxterAPIError, TyxterConnectionError

try:
    message = client.messages.create(payload, idempotency_key="order_123_send_1")
except TyxterAPIError as error:
    print(error.status_code, error.code, error.request_id, error.trace_id)
    if error.retry_after_ms is not None:
        print("retry after", error.retry_after_ms, "ms")
except TyxterConnectionError as error:
    print("request did not receive an API response", error)
```

`TyxterAPIError.body` preserves the original response. Internal errors may also
include `error.feedback`, which points to the public feedback endpoint.

## Webhook verification

Tyxter signs the exact raw request body with
`HMAC-SHA256(secret, "{timestamp}.{raw_body}")`. Never parse and re-serialize
the body before verification.

```python
from tyxter import WebhookSignatureVerifier

verifier = WebhookSignatureVerifier(signing_secret)
if not verifier.verify(raw_body=raw_body_bytes, headers=request_headers):
    raise PermissionError("invalid Tyxter webhook signature")
```

FastAPI:

```python
from fastapi import HTTPException, Request

@app.post("/webhooks/tyxter")
async def tyxter_webhook(request: Request) -> dict[str, bool]:
    raw_body = await request.body()
    if not verifier.verify(raw_body=raw_body, headers=request.headers):
        raise HTTPException(status_code=400, detail="invalid signature")
    return {"received": True}
```

Django:

```python
from django.http import HttpRequest, JsonResponse

def tyxter_webhook(request: HttpRequest) -> JsonResponse:
    headers = {key: value for key, value in request.headers.items()}
    if not verifier.verify(raw_body=request.body, headers=headers):
        return JsonResponse({"error": "invalid signature"}, status=400)
    return JsonResponse({"received": True})
```

Header names are case-insensitive. The default replay tolerance is 300 seconds.

## Media capability URLs

`client.media.upload(...)` performs create → capability upload → complete. The
SDK deliberately does not attach the Tyxter bearer token to the returned upload
URL. Capability failures raise `TyxterMediaUploadError`.

## Client ownership and cleanup

Use the context manager when the SDK creates its own `httpx.Client`. If you pass
`http_client=`, the caller retains ownership and the SDK will not close it.

```python
import httpx

http_client = httpx.Client()
client = Tyxter(api_key="tx_sandbox_...", http_client=http_client)
client.close()       # does not close http_client
http_client.close()  # caller-owned cleanup
```

`TyxterBootstrap` is a separate unauthenticated client for agent API-key device
authorization. It never sends a bearer token.

## Broadcast example

`examples/broadcast_customer_list.py` validates a CSV of E.164 phone numbers and
sends an approved template through `client.batches.create`.

```bash
python examples/broadcast_customer_list.py \
  --customers examples/customers.csv \
  --from pn_123 \
  --template-name promo_april \
  --template-language en_US \
  --name "April promo" \
  --idempotency-key idem_april_promo_001
```
