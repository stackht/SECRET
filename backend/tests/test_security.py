"""Tests for password hashing and JWT (Phase 2)."""
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("s3cret-password")
    assert hashed != "s3cret-password"
    assert verify_password("s3cret-password", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token("P-0421", extra={"role": "analyst"})
    claims = decode_token(token)
    assert claims["sub"] == "P-0421"
    assert claims["role"] == "analyst"
    assert "exp" in claims
    assert "iat" in claims
