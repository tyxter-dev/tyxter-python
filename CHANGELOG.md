# Changelog

All notable changes to the Tyxter Python SDK are documented here. The format is
based on Keep a Changelog, and versions follow Python packaging version rules.

**Version line.** This package shares its version number with the canonical
[`@tyxter/sdk-js`](https://www.npmjs.com/package/@tyxter/sdk-js), so a given
version means the same public route surface in both languages. That is why this
package goes `0.1.0a0` → `0.8.0` rather than incrementing from its own history:
it is adopting the canonical line, not claiming four releases of its own. Both
SDKs pin to the same `public-api-launch-endpoints.json` manifest through their
own conformance suites.

## [Unreleased]

These source changes are a draft candidate only; this section does not publish
an artifact to PyPI.

### Added

- Read-only `billing.list_phone_renewals()` and `billing.retrieve_phone_renewal()` from post-tag
  source commit `ed49c514b74a59de3b238d4ebc157f20482b6171`. They are not part of the published
  `sdk-js-v0.8.0` tag and remain Unreleased.

## [0.8.0] - 2026-09-01

This non-publishing Python source candidate ports published `sdk-js-v0.8.0`
(`58524926a1fa9498bcfe3abb9d7aa8fd39be1e85`). The `sdk-js-v0.7.0` tag was never published, so
npm 0.8.0 was the first artifact to carry both the 0.7 and 0.8 surfaces. These entries describe
API functionality and exact wire request, response, and webhook contracts while preserving
compatible Python call sites; they do not claim identical language-specific type construction.

### Added

- Project management, public feedback report reads, webhook endpoint test receipts, and optional
  project-scoped API-key creation.
- WhatsApp voice-note payloads, truthful unsupported/unknown inbound-message reads, phone-less
  inbound senders, media download hints, and media response fields without widening Instagram voice
  inputs or outbound identity requirements.
- Bounded transcription recovery with a required caller-supplied idempotency key, retry delay and
  API-discovery error details, `openai.stt` provider setup results, and typed transcription
  success/failure webhook contracts.
- Template authoring `parameter_format` response/request fields and standalone marketing
  `COPY_CODE` authoring, preserving the separate send-time variable and batch contracts.
- Phone-number `tier_2k`, nullable pending/durable Meta name-review observations, and public
  provider availability, WABA, and flow reconciliation observations without Python-side policy
  enforcement.
- Typed provider policy-warning and scheduled-disable webhook contracts with unchanged raw-body
  signature verification.
- Published contract and README truth for top-up and `credit.topped_up` response/event variants:
  `manual` and `promotion` payment/provider values, including intentionally omitted historical
  webhook providers. Promotion was not an item in the canonical changelog.

## [0.6.0] - 2026-08-10

This dated catch-up entry records the source version aligned to the published
JavaScript 0.5.0/0.6.0 surface. It does **not** claim that a Python 0.6.0
artifact has been published to PyPI.

### Added

- Message observability and capacity fields from the JavaScript 0.5.0 surface:
  `status_reason` on message responses, batch pacing forecasts, phone-number
  allowance estimates, and `messages.typing()` for an eligible inbound WhatsApp
  message.
- JavaScript 0.6.0's inbound-media and transcription surface: typed inbound
  media descriptors on message reads/lists, `media.list(source=...)`,
  `media.create_download_url()`, and request/retrieve transcription methods for
  inbound WhatsApp audio.
- Typed native WhatsApp `order_details` messages with Brazil Pix dynamic-code
  settings, structured phone recipients, and current provider-connection
  eligibility/restriction fields.

At the historical published-JavaScript 0.5/0.6 parity checkpoint, both SDK
sources exposed **170 of 172** manifest routes. The shared exemptions are
`PUT` and `GET /v1/media/blobs/:token`: their signed capability token is the
sole authority, so neither SDK wraps them in a bearer-authenticated method.

## [0.4.0] - 2026-08-03

First published release, and the point at which this package adopts the
canonical version line.

Verified at parity with `@tyxter/sdk-js` 0.4.0: both cover an identical **166 of
168** manifest routes, no route is covered by one SDK and missing from the
other, and neither invents a route the manifest does not define. The two
uncovered routes are the capability-token media blob `GET`/`PUT` endpoints,
exempt in both SDKs because the signed URL is the sole authority and neither
wraps it in a bearer-auth method.

### Changed

- The SDK now develops in its own repository,
  [`tyxter-dev/tyxter-python`](https://github.com/tyxter-dev/tyxter-python),
  instead of living under `sdks/python` in the Tyxter Messaging monorepo. The
  published package name (`tyxter`), its import path, and its public API are
  unchanged — this move affects contributors, not consumers.
- The canonical public-API manifest is vendored under `conformance/` and kept
  current by an automated sync PR from the Tyxter Messaging repo. The route,
  header, and query-parameter conformance gates are unchanged in strength.
- Release tags are `v<version>`, not `sdk-python-v<version>`.
- The client User-Agent assertion derives from `__version__` instead of a
  hardcoded literal, so a version bump is no longer a test failure.

### Added

- Typed synchronous `Tyxter` client for Python 3.10–3.13.
- Full public launch-manifest resource coverage, including channel-native
  message helpers, media capability uploads, webhook event listening, billing,
  automations, LLM routes, and agentic payments.
- Unauthenticated `TyxterBootstrap` client for agent API-key device approval.
- Typed stable API errors and cross-language webhook signature verification.
- Route, distribution, strict typing, and multi-version CI conformance gates.
- Query-parameter conformance gate: every method's query surface is locked to
  the Zod-derived `public-api-query-params.json` snapshot, so a contract query
  schema gaining a field fails the suite until the SDK exposes it.
- `messages.list()` server-side `direction` filter and typed
  `include="payload"` expansion.
- `data_retention` policy resource, `sandbox.llm.set_failure()` failure
  injection, and `provider_connections.complete_meta_registration()`.
- Typed `meta_signup_sessions.create()` / `.retrieve()` coverage and a parity
  gate between the typed and runtime error-type allowlists.

## [0.1.0a0] - 2026-07-14

Never published to PyPI — an in-tree marker from when the package lived in the
monorepo, kept here for history.

### Added

- Initial in-tree alpha package scaffold.
