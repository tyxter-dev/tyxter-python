# Tyxter Python SDK

Typed, synchronous Python client for the Tyxter Messaging API. The package uses
`httpx`, supports Python 3.10–3.13, and covers every SDK-callable route in the
public launch manifest.

The SDK is alpha software. Additive response fields are compatible and are
tolerated at runtime. Removing or renaming a public method, field, or stable
`error.code` requires a deprecation cycle.

The `0.6.0` source line is a draft candidate. Editing the version or these docs
does not publish a package, create a tag, or change PyPI state.

## Install

`pip install tyxter` installs the latest artifact currently published on PyPI.
It may not include the draft 0.6 APIs documented in this checkout. To evaluate
the candidate, check out its branch or commit and install that checkout into the
project environment:

```bash
git clone https://github.com/tyxter-dev/tyxter-python.git
cd tyxter-python
git checkout CANDIDATE_COMMIT_OR_BRANCH
uv sync --locked --extra dev
uv run python -c "import tyxter; print(tyxter.__version__)"
```

For routine development checks in that environment:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
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

## Native Pix order details

WhatsApp interactive sends accept the existing button/list payloads and the typed
native `order_details` Pix variant. A recipient can remain an E.164 string or use
the structured calling-code form; the SDK sends the latter unchanged as the public
API's `country_calling_code` and `national_number` fields.

```python
client.whatsapp.send_interactive(
    {
        "from": sender_id,
        "to": {"country_calling_code": "55", "national_number": "11999999999"},
        "interactive": {
            "type": "order_details",
            "header": {"type": "image", "link": "https://cdn.example.test/order.png"},
            "body": {"text": "Review and pay"},
            "footer": {"text": "Tyxter Store"},
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
                                "code": "000201010212",
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
        },
    }
)
```

Native Pix order details are for a Brazil WABA eligible for Meta's Payments API.
The API accepts the request after its own checks, but Meta evaluates WABA and
message eligibility at provider-send time, so acceptance does not promise
delivery. This interactive message has no Tyxter `payment_id` resolution or
order-status update, and Meta does not reconcile settlement; confirm settlement
with the merchant or PSP.

## Inbound audio transcription and retries

Use `messages.request_transcription(message_id, {"language": "pt"})` to opt an
inbound WhatsApp-audio message into asynchronous transcription, then poll the
same receipt with `messages.retrieve_transcription(message_id)`. The typed
receipt exposes `pending`, `succeeded`, or `failed`, its text/error fields, and
its `trace_id`. A pending or succeeded request replays its receipt only when the
language is omitted or matches; a failed receipt returns
`transcription_retry_required`.

Requesting transcription never buys a second attempt. Start one bounded manual
retry only with `messages.retry_transcription()`. Its caller-supplied, nonblank
idempotency key is trimmed before sending; reuse that same key to replay the
accepted retry without opening another generation. A retry always reuses the
original source; it cannot replace media that has expired or is structurally
unavailable. If the API returns `transcription_retry_rate_limited`, wait its
`retry_after_ms` value and replay the same logical retry command with the same
key. Use a fresh key only for a distinct retry command.

Subscribe to both terminal events: `message.media_transcribed` and
`message.media_transcription_failed`. The success event carries the transcript's
speech, provider, model, and duration; the failure event is failure-safe and
carries its stable `error_code` without those success-only fields.

```python
client.messages.retry_transcription(
    "msg_123",
    {"language": "pt"},
    idempotency_key="transcription-retry-msg_123-1",
    trace_id="trc_transcription_retry",
)
```

## Inbound media, typing, and message observability

Inbound message reads and lists expose a typed `media` descriptor with the
Tyxter `mda_*` asset ID. Use `client.media.list(source="inbound_provider")` to
find imported provider media and `client.media.create_download_url(asset_id)`
to mint a fresh, short-lived `download_url`; do not assume a previous capability
URL remains valid. A consumed inbound descriptor also has a `download` hint
(`{"method": "GET", "path": ...}`); treat it as the API's current download
affordance rather than a durable provider URL. Failed media carries `failure`,
while expired and deleted media carry neither a download nor a failure.

For WhatsApp OGG/Opus mono audio, `client.whatsapp.send_media(...)` accepts
`"voice": True` to request a native voice note; omit it or pass `False` for
ordinary audio. Instagram media has a separate input shape: ordinary image,
document, audio, and video sends remain valid, but it deliberately has no
`voice` field. An inbound WhatsApp sender can be phone-less, represented on
reads only as `{"type": "phone_e164", "id": ""}`; do not reuse it as an
outbound recipient. `type == "unsupported"` means the provider withheld the
content and supplies an `unsupported` descriptor when available, whereas
`type == "unknown"` means content arrived but has no typed projection yet—read
its raw `payload` through `retrieve()` or `list(include="payload")` instead of
treating it as a refusal. A default list row may have `payload` set to `None`.

For a WhatsApp typing indicator, pass the Tyxter message ID from
`message.received.data.message_id`. The webhook envelope's top-level `id` is the
event ID and `data.provider_message_id` is Meta's reference, so neither targets
`client.messages.typing()`. The indicator response is an `accepted` receipt.

Message accepts and reads expose `trace_id` for correlation. `retrieve()` also
returns the message event timeline, while message rows expose `status_reason`,
terminal error details, provider error information, and
`delivery_unconfirmed_at` when provider acceptance has not yet been followed by
a delivery status. An accepted send is not a delivery guarantee.

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

- `account`, `api_keys`, `ai_agents`, `agentic_payments`, `audiences`, and `projects`
- `automations`, `automation_runs`, and `automation_webhooks`
- `batches`, `billing`, `contacts`, `data_retention`, `feedback`, `fiscal`,
  and `flows`
- `llm`, `llm_routes`, `media`, `messages`, `meta_signup_sessions`, and `payments`
- `phone_numbers`, `provider_connections`, and
  `provider_credential_setup_sessions`
- `rate_cards`, `sandbox`, `templates`, `usage`, `webhook_endpoints`, and
  `webhook_events`
- channel-native conveniences: `whatsapp`, `instagram`, and
  `whatsapp_channels`

Request and response dictionaries are `TypedDict` contracts exported from
`tyxter.types`. Write methods expose `idempotency_key` and `trace_id` only where
the canonical endpoint manifest supports those headers.

Provider credential setup keeps `create()` and `retrieve()` source-compatible
with `ProviderCredentialSetupSessionResponse`, including mutable status and
completion fields. Use `create_result()` or `retrieve_result()` when strict type
narrowing must distinguish provider-connection, TTS, and STT completion axes.

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

- **Unsupported** endpoints do not expose an idempotency-key argument because
  the manifest disallows that header.
- **Supported** endpoints accept an optional caller key and forward it when one
  is supplied.
- **Required** endpoints always send a key. `feedback.create()` generates one
  when omitted (and rejects an explicit blank key); transcription retry requires
  the caller to supply a nonblank key.

Flow creation, LLM route upsert/delete, AI Agent completion, and automation
webhook-secret rotation all accept the `idempotency_key` keyword argument.

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
include `error.feedback`, which points to the public feedback endpoint. A
`route_not_found` response may instead include `error.discovery`, whose
`openapi` and `well_known` relative paths describe the API host; read it from
the raw body rather than expecting a separate exception attribute.

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

## Route conformance

`conformance/` holds a vendored copy of the canonical public-API manifest:

- `public-api-launch-endpoints.json` — every launch route, its scope, query
  schema, and whether it honors `Idempotency-Key` / `Trace-Id`.
- `public-api-query-params.json` — the Zod-derived query-parameter names.
- `SOURCE_COMMIT` — the Tyxter Messaging commit these copies were taken from.

`tests/test_route_conformance.py` pins this package's resource surface to that
manifest: a route in the manifest with no typed SDK method fails, an SDK method
that hits a route the manifest does not define fails, and a query parameter or
`Idempotency-Key` mode (`unsupported`, `supported`, or `required`) that drifts
from the contract fails.

The current source is a draft candidate covering **179 of 181** manifest rows.
The two reviewed shared exemptions are `PUT` and
`GET /v1/media/blobs/:token`: each uses its signed capability token as the sole
authority and is intentionally not a bearer-authenticated SDK method. This count
is source-conformance evidence, not a publication claim.

**Do not hand-edit these files to make a test pass.** They are generated in the
Tyxter Messaging repo, where they are verified against the mounted `v1`
controllers, and are updated here only by the automated sync PR. Editing them
locally silences the gate instead of fixing the drift — if a sync PR turns the
suite red, the correct fix is to add or correct the SDK method.
