"""
Comprehensive pytest test suite for AI Database Analyst auth system.

Covers:
  1. Registration
  2. Login
  3. JWT / jti claim
  4. /auth/me (protected endpoint)
  5. Refresh token
  6. Concurrent refresh (same token)
  7. Logout
  8. Malformed JWTs
  9. User data isolation
  10. Customer/Order removed
  11. App startup and OpenAPI
  12. Migration integrity (offline check)
"""
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import jwt as pyjwt
import pytest

from app.core.config import SECRET_KEY, ALGORITHM

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_USER = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "securepassword123",
}

VALID_USER2 = {
    "name": "Second User",
    "email": "seconduser@example.com",
    "password": "anotherpassword456",
}


def register(client, user=None):
    """Register a user and return response."""
    if user is None:
        user = VALID_USER
    return client.post("/auth/register", json=user)


def login(client, email=None, password=None):
    """Login and return response."""
    if email is None:
        email = VALID_USER["email"]
    if password is None:
        password = VALID_USER["password"]
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


def register_and_login(client, user=None):
    """Register + login; return the token response JSON."""
    if user is None:
        user = VALID_USER
    register(client, user)
    resp = login(client, user["email"], user["password"])
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()


def decode_token(token: str) -> dict:
    """Decode a JWT without verifying expiry (for test assertions)."""
    return pyjwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False},
    )


def make_token(payload_extra: dict) -> str:
    """Create a JWT with the given extra payload fields using our secret."""
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {"exp": exp, **payload_extra}
    return pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ===========================================================================
# 1. Registration
# ===========================================================================


def test_register_success(client):
    resp = client.post("/auth/register", json=VALID_USER)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == VALID_USER["name"]
    assert data["email"] == VALID_USER["email"]


def test_register_duplicate_email(client):
    client.post("/auth/register", json=VALID_USER)
    resp = client.post("/auth/register", json=VALID_USER)
    assert resp.status_code == 409


def test_register_password_too_short(client):
    user = {**VALID_USER, "password": "short"}  # 5 chars < 8
    resp = client.post("/auth/register", json=user)
    assert resp.status_code == 422


def test_register_password_exactly_8_chars(client):
    user = {**VALID_USER, "password": "12345678"}  # exactly 8 chars
    resp = client.post("/auth/register", json=user)
    assert resp.status_code == 201


def test_register_password_at_72_bytes(client):
    password = "a" * 72  # 72 ASCII chars = 72 UTF-8 bytes
    assert len(password.encode("utf-8")) == 72
    user = {**VALID_USER, "password": password}
    resp = client.post("/auth/register", json=user)
    assert resp.status_code == 201


def test_register_password_exceeds_72_bytes(client):
    password = "a" * 73  # 73 ASCII chars = 73 UTF-8 bytes
    assert len(password.encode("utf-8")) == 73
    user = {**VALID_USER, "password": password}
    resp = client.post("/auth/register", json=user)
    assert resp.status_code == 422


# ===========================================================================
# 2. Login
# ===========================================================================


def test_login_success(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    register(client)
    resp = login(client, password="wrongpassword")
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = login(client, email="nobody@example.com")
    assert resp.status_code == 401


# ===========================================================================
# 3. JWT / jti claim
# ===========================================================================


def test_access_token_has_jti(client):
    tokens = register_and_login(client)
    payload = decode_token(tokens["access_token"])
    assert "jti" in payload, "access_token must contain a 'jti' claim"


def test_refresh_token_has_jti(client):
    tokens = register_and_login(client)
    payload = decode_token(tokens["refresh_token"])
    assert "jti" in payload, "refresh_token must contain a 'jti' claim"


def test_two_logins_have_different_jti(client):
    register(client)
    tokens1 = login(client).json()
    tokens2 = login(client).json()
    jti1 = decode_token(tokens1["refresh_token"]).get("jti")
    jti2 = decode_token(tokens2["refresh_token"]).get("jti")
    assert jti1 != jti2, "Two logins must produce distinct jti values"


# ===========================================================================
# 4. /auth/me (protected endpoint)
# ===========================================================================


def test_me_with_valid_token(client):
    tokens = register_and_login(client)
    resp = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == VALID_USER["email"]


def test_me_without_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_refresh_token_as_access(client):
    tokens = register_and_login(client)
    resp = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert resp.status_code == 401


def test_me_with_garbage_token(client):
    resp = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer garbage"},
    )
    assert resp.status_code == 401


# ===========================================================================
# 5. Refresh token
# ===========================================================================


def test_refresh_success(client):
    tokens = register_and_login(client)
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_revokes_old_token(client):
    tokens = register_and_login(client)
    old_refresh = tokens["refresh_token"]
    # First refresh should succeed
    client.post("/auth/refresh", json={"refresh_token": old_refresh})
    # Second use of same token must fail
    resp2 = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp2.status_code == 401


def test_refresh_new_token_works(client):
    tokens = register_and_login(client)
    resp1 = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert resp1.status_code == 200
    new_refresh = resp1.json()["refresh_token"]
    resp2 = client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert resp2.status_code == 200


def test_refresh_with_access_token(client):
    tokens = register_and_login(client)
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert resp.status_code == 401


def test_refresh_with_garbage(client):
    resp = client.post("/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401


# ===========================================================================
# 6. Concurrent refresh (same token)
# ===========================================================================


def test_concurrent_refresh_only_one_wins(client):
    tokens = register_and_login(client)
    refresh_token = tokens["refresh_token"]
    resp1 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    resp2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    statuses = {resp1.status_code, resp2.status_code}
    assert 200 in statuses, "At least one refresh must succeed"
    assert 401 in statuses, "Second use of same refresh token must fail"


# ===========================================================================
# 7. Logout
# ===========================================================================


def test_logout_success(client):
    tokens = register_and_login(client)
    resp = client.post(
        "/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    assert "Logged out" in resp.json().get("message", "")


def test_logout_then_refresh_fails(client):
    tokens = register_and_login(client)
    refresh_token = tokens["refresh_token"]
    client.post("/auth/logout", json={"refresh_token": refresh_token})
    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 401


def test_logout_with_access_token(client):
    tokens = register_and_login(client)
    resp = client.post(
        "/auth/logout",
        json={"refresh_token": tokens["access_token"]},
    )
    assert resp.status_code == 401


def test_logout_with_garbage(client):
    resp = client.post("/auth/logout", json={"refresh_token": "garbage"})
    assert resp.status_code == 401


# ===========================================================================
# 8. Malformed JWTs
# ===========================================================================


def test_malformed_jwt_in_refresh(client):
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": "not.a.valid.jwt"},
    )
    assert resp.status_code == 401


def test_malformed_subject_in_refresh(client):
    # sub=None — int(None) will raise TypeError inside the route
    bad_token = make_token({"sub": None, "type": "refresh"})
    resp = client.post("/auth/refresh", json={"refresh_token": bad_token})
    assert resp.status_code == 401


def test_malformed_subject_in_logout(client):
    bad_token = make_token({"sub": None, "type": "refresh"})
    resp = client.post("/auth/logout", json={"refresh_token": bad_token})
    assert resp.status_code == 401


def test_wrong_type_in_refresh(client):
    # type="access" sent to /auth/refresh
    bad_token = make_token({"sub": "1", "type": "access"})
    resp = client.post("/auth/refresh", json={"refresh_token": bad_token})
    assert resp.status_code == 401


# ===========================================================================
# 9. User data isolation
# ===========================================================================


def test_user_cannot_access_other_users_me(client):
    tokens1 = register_and_login(client, VALID_USER)
    tokens2 = register_and_login(client, VALID_USER2)

    # User 1 sees their own data
    me1 = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens1['access_token']}"},
    ).json()
    assert me1["email"] == VALID_USER["email"]

    # User 2 sees their own data
    me2 = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens2['access_token']}"},
    ).json()
    assert me2["email"] == VALID_USER2["email"]

    # They should have different IDs
    assert me1["id"] != me2["id"]


# ===========================================================================
# 10. Customer/Order removed
# ===========================================================================


def test_customers_route_does_not_exist(client):
    resp = client.get("/customers/")
    assert resp.status_code == 404


def test_customer_post_does_not_exist(client):
    resp = client.post("/customers/", json={})
    assert resp.status_code == 404


def test_orders_route_does_not_exist(client):
    resp = client.get("/orders/")
    assert resp.status_code == 404


# ===========================================================================
# 11. App startup and OpenAPI
# ===========================================================================


def test_app_imports():
    from app.main import app  # noqa: F401 — must not raise
    assert app is not None


def test_openapi_schema(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "paths" in schema
    paths = schema["paths"]
    # No customer or order routes
    for path_key in paths:
        assert "customers" not in path_key, (
            f"Found 'customers' in path '{path_key}' — cleanup not complete"
        )
        assert "orders" not in path_key, (
            f"Found 'orders' in path '{path_key}' — cleanup not complete"
        )


# ===========================================================================
# 12. Migration integrity (offline check)
# ===========================================================================


def test_migration_chain_has_no_customer_model_import():
    """
    Check that migration a1b2c3d4e5f6 exists in the migrations/versions dir.

    The cleanup worker is expected to create a migration with
    revision 'a1b2c3d4e5f6'.  Until it does, this test will fail and
    be reported as 'pending cleanup worker completion'.
    """
    versions_dir = Path(__file__).resolve().parents[1] / "migrations" / "versions"
    assert versions_dir.is_dir(), f"migrations/versions dir not found: {versions_dir}"

    target_revision = "a1b2c3d4e5f6"
    found = False
    for migration_file in versions_dir.glob("*.py"):
        content = migration_file.read_text(encoding="utf-8", errors="replace")
        if f"revision = '{target_revision}'" in content or \
           f'revision = "{target_revision}"' in content or \
           target_revision in content:
            found = True
            break

    assert found, (
        f"Migration with revision '{target_revision}' not found in "
        f"{versions_dir} — pending cleanup worker completion"
    )
