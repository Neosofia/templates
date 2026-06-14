"""
Cedar principal for REST-inferred ``@with_security`` routes.

Document resources are built from ``src.models.document``; only the principal
is service-specific. JWT → principal mapping uses the SDK helper (including
``neosofia:principal_type`` for demo Patient/Clinician tokens and
``neosofia:actors`` for Tier-1 platform operators; ``neosofia:roles`` for Tier-2 org roles).
"""
from __future__ import annotations

from typing import Any

from flask import g

from authorization_in_the_middle.flask_identity import jwt_claim_principal_attributes, resolve_jwt_principal

NAMESPACE = "demo"

_DEMO_CLINICIAN_ATTRS = ("role", "clinic_id")


def resolve_principal() -> dict[str, Any]:
    claims = getattr(g, "jwt_claims", None) or {}
    _, _, jwt_attrs = jwt_claim_principal_attributes(claims, default_type="User")
    extra_attrs = {
        attr: jwt_attrs[attr]
        for attr in _DEMO_CLINICIAN_ATTRS
        if attr in jwt_attrs
    }
    return resolve_jwt_principal(
        NAMESPACE,
        default_type="User",
        extra_attrs=extra_attrs or None,
    )
