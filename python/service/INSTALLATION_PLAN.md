# Product Installation Plan

Per-version instructions for system administrators: prerequisites, deploy and configuration steps, post-deploy verification, and evidence to capture. For what changed in each release, see [CHANGELOG.md](CHANGELOG.md).

## python-template v0.10.3

**Build identifiers:** **python-template v0.10.3**; SDK **`authorization-in-the-middle/v0.7.6`**.

**Prerequisites:**

- None beyond the prior release.

**Deploy:**

1. Pull `ghcr.io/neosofia/python-template:v0.10.3` (tag `python-template/v0.10.3`).
2. Deploy with existing env unchanged.

**Post-deploy verification:**

1. `GET /health` returns `"status": "ok"` and `"version": "0.10.3"`.

**Evidence:** Health JSON.

---

## python-template v0.10.2

**Build identifiers:** **python-template v0.10.2**; SDK **`authorization-in-the-middle/v0.7.6`**.

**Prerequisites:**

- None beyond the prior release.

**Deploy:**

1. Pull `ghcr.io/neosofia/python-template:v0.10.2` (tag `python-template/v0.10.2`).
2. Deploy with existing env unchanged.

**Post-deploy verification:**

1. `GET /health` returns `"status": "ok"` and `"version": "0.10.2"`.

**Evidence:** Health JSON.

---

## python-template v0.10.1

**Build identifiers:** **python-template v0.10.1**; SDK **`authorization-in-the-middle/v0.7.2`**.

**Prerequisites:**

- None beyond the prior release.

**Deploy:**

1. Pull `ghcr.io/neosofia/python-template:v0.10.1` (tag `python-template/v0.10.1`).
2. Deploy with existing env unchanged.

**Post-deploy verification:**

1. `GET /health` returns `"status": "ok"` and `"version": "0.10.1"`.
2. Clinician JWT with matching `neosofia:clinic_id` can `GET /api/v1/documents/{id}/summary`.
3. Clinic admin clinician JWT can `DELETE /api/v1/documents/{id}`; non-admin clinician delete still returns **403**.

**Evidence:**

- Health version matches **0.10.1**.
- Document read, summary, and delete smoke checks pass.

## python-template v0.9.0

**Build identifiers:** **python-template v0.9.0**; SDK **`authorization-in-the-middle/v0.4.23`**.

**Prerequisites:**

- None beyond the prior release.

**Deploy:**

1. Pull `ghcr.io/neosofia/python-template:v0.9.0` (tag `python-template/v0.9.0`).
2. Deploy with existing env unchanged.

**Post-deploy verification:**

1. `GET /health` returns `"status": "ok"` and `"version": "0.9.0"`.
2. Authorized JWT can `GET /api/v1/documents/{id}`; unauthorized delete still returns **403**.

**Evidence:**

- Health version matches **0.9.0**.
- Document read and delete smoke checks pass.
