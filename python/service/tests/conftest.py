import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# Generate keys at module load time so they exist before ANY test imports
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()

_PRIVATE_PEM = _PRIVATE_KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

_PUBLIC_PEM = _PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

os.environ["JWT_PUBLIC_KEY"] = _PUBLIC_PEM.decode()
os.environ["JWT_ISSUER"] = "https://test.neosofia.com"
os.environ["JWT_AUDIENCE"] = "api.test.neosofia.com"

@pytest.fixture(scope="session")
def rsa_keypair():
    return {"private": _PRIVATE_PEM, "public": _PUBLIC_PEM}

