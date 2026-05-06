# Security Notes

This template is intended to encode the default security baseline for new Python services.

## Controls Included

- HTTPS enforcement outside development and test.
- `Content-Security-Policy`, `Strict-Transport-Security`, and `Referrer-Policy` headers.
- Explicit `ProxyFix` hop-count configuration.
- Application-level request body size cap.
- Generic JSON error payloads for invalid requests, missing resources, and authorization failures.
- Structured JSON logs via `logenvelope`.
- Fail-closed authorization with in-process Cedar evaluation.
- Rate limiting with a configurable shared backend.

## Logging Rules

- Do not log PHI, PII, or SPII.
- Log exception types rather than raw exception strings.
- Use machine-readable event names for lifecycle and error events.

## Deployment Notes

- Replace the local `authorization-in-the-middle` source override with an immutable release artifact before publishing or deploying a copied template.
- Use Redis or another shared backend for rate limiting in multi-replica environments.
