import pytest
import jwt
from datetime import datetime, timezone, timedelta
from main import app

pytestmark = pytest.mark.unit

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def _secure_request(client, rsa_keypair, method: str, path: str, claims: dict = None, **kwargs):
    if claims:
        # Default mandatory claims
        base_claims = {
            "iss": "https://test.neosofia.com",
            "aud": "api.test.neosofia.com",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp())
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
        claims={
            "sub": "p1",
            "neosofia:token_type": "human",
            "neosofia:roles": ["patient"]
        }
    )
    assert response.status_code == 200
    assert response.get_json()["document_id"] == "d1"

def test_clinician_can_read_summary_with_same_capability(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "GET", "/api/v1/documents/d1/summary",
        claims={
            "sub": "c1",
            "neosofia:token_type": "human",
            "neosofia:roles": ["physician", "clinician"],
            "neosofia:tenant_id": "clinic-a"
        }
    )
    assert response.status_code == 200
    assert "summary" in response.get_json()

def test_non_admin_clinician_delete_is_denied(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "DELETE", "/api/v1/documents/d1",
        claims={
            "sub": "c1",
            "neosofia:token_type": "human",
            "neosofia:roles": ["physician", "clinician"],
            "neosofia:tenant_id": "clinic-a"
        }
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "forbidden"

def test_admin_clinician_delete_is_allowed(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "DELETE", "/api/v1/documents/d1",
        claims={
            "sub": "c-admin",
            "neosofia:token_type": "human",
            "neosofia:roles": ["admin", "clinician"],
            "neosofia:tenant_id": "clinic-a"
        }
    )
    assert response.status_code == 200
    assert response.get_json()["deleted"] == "d1"

def test_missing_valid_jwt_returns_401(client, rsa_keypair):
    # Sends no auth at all
    response = _secure_request(
        client, rsa_keypair, "GET", "/api/v1/documents/d1"
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthenticated"

def test_missing_document_returns_404(client, rsa_keypair):
    response = _secure_request(
        client, rsa_keypair, "GET", "/api/v1/documents/missing",
        claims={
            "sub": "p1",
            "neosofia:token_type": "human",
            "neosofia:roles": ["patient"]
        }
    )
    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"

def test_health_is_unauthenticated(client, rsa_keypair):
    # Health checks don't require JWT usually
    response = _secure_request(client, rsa_keypair, "GET", "/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_security_headers_are_present(client, rsa_keypair):
    response = _secure_request(client, rsa_keypair, "GET", "/health")
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
