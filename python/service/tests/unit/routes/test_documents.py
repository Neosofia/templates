from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
import pytest

pytestmark = pytest.mark.unit


def _secure_request(client, rsa_keypair, method: str, path: str, claims: Optional[dict] = None, **kwargs):
    if claims:
        base_claims = {
            "iss": "https://test.neosofia.com",
            "aud": "python-template",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
            "neosofia:roles": ["user"],
        }
        base_claims.update(claims)

        token = jwt.encode(base_claims, rsa_keypair["private"], algorithm="RS256")

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers

    return client.open(path, method=method, base_url="https://localhost", **kwargs)


def test_patient_can_read_own_document(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "GET", "/api/v1/documents/d1",
        claims={"sub": "p1", "neosofia:principal_type": "Patient"},
    )
    assert response.status_code == 200
    assert response.get_json()["document_id"] == "d1"


def test_clinician_can_read_summary_with_same_capability(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "GET", "/api/v1/documents/d1/summary",
        claims={"sub": "c1", "neosofia:principal_type": "Clinician", "neosofia:role": "physician", "neosofia:clinic_id": "clinic-a"},
    )
    assert response.status_code == 200
    assert "summary" in response.get_json()


def test_non_admin_clinician_delete_is_denied(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "DELETE", "/api/v1/documents/d1",
        claims={"sub": "c1", "neosofia:principal_type": "Clinician", "neosofia:role": "clinician", "neosofia:clinic_id": "clinic-a"},
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "forbidden"


def test_admin_clinician_delete_is_allowed(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "DELETE", "/api/v1/documents/d1",
        claims={"sub": "c-admin", "neosofia:principal_type": "Clinician", "neosofia:role": "admin", "neosofia:clinic_id": "clinic-a"},
    )
    assert response.status_code == 200
    assert response.get_json()["deleted"] == "d1"


def test_operator_can_read_document(client, rsa_keypair):
    response = _secure_request(
        client,
        rsa_keypair,
        "GET",
        "/api/v1/documents/d1",
        claims={"sub": "019e02b4-47e1-778a-9331-476e9f927bd9", "neosofia:actors": ["operator"]},
    )
    assert response.status_code == 200
    assert response.get_json()["document_id"] == "d1"


def test_missing_valid_jwt_returns_401(client, rsa_keypair):
    response = _secure_request(client, rsa_keypair, "GET", "/api/v1/documents/d1")
    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthenticated"


def test_missing_document_returns_404(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "GET", "/api/v1/documents/missing",
        claims={"sub": "p1", "neosofia:principal_type": "Patient"},
    )
    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_security_headers_are_present(client, rsa_keypair):
    response = _secure_request(client, rsa_keypair, "GET", "/health")
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
