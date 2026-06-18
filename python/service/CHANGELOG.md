# Changelog

What changed for people who use or depend on this service (operators, integrators, clinicians -- not deploy runbooks). Configuration and verification: [INSTALLATION_PLAN.md](INSTALLATION_PLAN.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.10.2] - 2026-06-18

### Fixed

- Service errors and API failures are recorded in operational logs at default verbosity.

## [0.10.1] - 2026-06-14

### Fixed

- Demo clinician Cedar principal forwards ``neosofia:role`` and ``neosofia:clinic_id`` via ``extra_attrs`` so clinic-scoped read/delete policies evaluate correctly.

### Changed

- Pinned **`authorization-in-the-middle/v0.7.2`** (``/summary`` member subresource inference).

## [0.10.0] - 2026-06-14

### Changed

- Pinned **`authorization-in-the-middle/v0.7.1`**; principals via shared `resolve_jwt_principal`.

## [0.9.0] - 2026-06-10

### Changed

- Document routes use bare `@with_security()` with `resource_loader` only — REST inference supplies Cedar actions; no `Capabilities` indirection.
- Pinned **`authorization-in-the-middle/v0.4.23`** and **`logenvelope/v0.3.4`**.

### Removed

- `src/bootstrap/capabilities.py` — action strings belong in Cedar policy or inline `action='Action::"…"'` when inference cannot apply.
