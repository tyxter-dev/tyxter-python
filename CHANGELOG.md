# Changelog

All notable changes to the Tyxter Python SDK are documented here. The format is
based on Keep a Changelog, and versions follow Python packaging version rules.

**Version line.** This package shares its version number with the canonical
[`@tyxter/sdk-js`](https://www.npmjs.com/package/@tyxter/sdk-js), so a given
version means the same public route surface in both languages. That is why this
package goes `0.1.0a0` → `0.4.0` rather than incrementing from its own history:
it is adopting the canonical line, not claiming four releases of its own. Both
SDKs pin to the same `public-api-launch-endpoints.json` manifest through their
own conformance suites.

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
