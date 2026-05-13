from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
import pytest

pytestmark = pytest.mark.integration


def _get_token(rsa_keypair, claims: Optional[dict] = None) -> str:
    base_claims = {
        "iss": "https://test.neosofia.com",
        "aud": "python-template",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        "sub": "p1",
        "neosofia:principal_type": "Patient",
        "neosofia:roles": ["user"],
    }
    if claims:
        base_claims.update(claims)
    return jwt.encode(base_claims, rsa_keypair["private"], algorithm="RS256")


def test_document_response_matches_contract(client, api_spec, validate_response, rsa_keypair):
    token = _get_token(rsa_keypair)
    response = client.get(
        "/api/v1/documents/d1",
        base_url="https://localhost",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/documents/{document_id}", "get", 200, response.get_json())


def test_error_response_matches_contract(client, api_spec, validate_response):
    response = client.get("/api/v1/documents/d1", base_url="https://localhost")

    assert response.status_code == 401
    validate_response(api_spec, "/api/v1/documents/{document_id}", "get", 401, response.get_json())
