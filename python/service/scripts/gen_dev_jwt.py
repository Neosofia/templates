#!/usr/bin/env python3
"""
Utility script to generate an RSA Keypair, a valid RS256 JWT,
and instructions for configuring the local service to accept it.
"""
import sys
import json
import base64
import argparse
from datetime import datetime, timezone, timedelta

try:
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("Error: Missing pyjwt or cryptography.")
    print("Make sure you are running this from within the service's uv virtual environment:")
    print("uv run scripts/gen_dev_jwt.py")
    sys.exit(1)

def generate():
    parser = argparse.ArgumentParser(description="Generate a dev JWT")
    parser.add_argument("--sub", default="p1", help="The subject (principal ID)")
    parser.add_argument("--type", default="Patient", help="The principal type (Patient, Clinician, etc.)")
    parser.add_argument("--claims", type=str, help="Optional raw JSON string for additional neosofia:* claims")
    args = parser.parse_args()

    print("Generating 2048-bit RSA keypair...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    public_b64 = base64.b64encode(public_pem).decode('utf-8')

    base_claims = {
        "iss": "https://neosofia.com",
        "aud": "api.neosofia.com",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp()),
        "sub": args.sub,
        "neosofia:principal_type": args.type
    }

    if args.claims:
        try:
            extra = json.loads(args.claims)
            for k, v in extra.items():
                if not k.startswith("neosofia:"):
                    base_claims[f"neosofia:{k}"] = v
                else:
                    base_claims[k] = v
        except Exception as e:
            print(f"Warning: Failed to parse extra claims JSON: {e}")

    token = jwt.encode(base_claims, private_pem, algorithm="RS256")

    print("\n" + "="*60)
    print("✅ DEV JWT CREATED")
    print("="*60 + "\n")
    
    print("1. Add this to your local .env file so the service trusts the signature:\n")
    print(f"JWT_PUBLIC_KEY={public_b64}")
    
    print("\n2. Use this Bearer Token in your requests (Valid for 30 days):\n")
    print(token)
    
    print("\nExample cURL:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8018/api/v1/documents/d1')

if __name__ == '__main__':
    generate()
