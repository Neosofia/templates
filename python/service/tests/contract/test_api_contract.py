import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import jwt

import pytest
from jsonschema import validate

from main import app


pytestmark = pytest.mark.contract


def _schema(name: str) -> dict:
    root = Path(__file__).resolve().parents[2]
    spec = json.loads((root / "openapi.json").read_text())
    return spec["components"]["schemas"][name]


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def _get_token(rsa_keypair, claims=None):
    base_claims = {
        "iss": "https://test.neosofia.com",
        "aud": "api.test.neosofia.com",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        "sub": "p1",
        "neosofia:token_type": "human",
        "neosofia:roles": ["patient"]
    }
    if claims:
        base_claims.update(claims)
    return jwt.encode(base_claims, rsa_keypair["private"], algorithm="RS256")

def test_health_response_matches_contract(client):
    response = client.get("/health", base_url="https://localhost")

    assert response.status_code == 200
    validate(instance=response.get_json(), schema=_schema("HealthResponse"))


def test_document_response_matches_contract(client, rsa_keypair):
    token = _get_token(rsa_keypair)
    response = client.get(
        "/api/v1/documents/d1",
        base_url="https://localhost",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    validate(instance=response.get_json(), schema=_schema("DocumentResponse"))


def test_error_response_matches_contract(client, rsa_keypair):
    # Use valid token but invalid auth payload? Or just test with NO token which throws a 401 error response 
    response = client.get(
        "/api/v1/documents/d1",
        base_url="https://localhost",
    )

    assert response.status_code == 401
    validate(instance=response.get_json(), schema=_schema("ErrorResponse"))

