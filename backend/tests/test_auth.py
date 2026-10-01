"""Pytest suite for OpsAI authentication."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User, UserRole


def test_hash_and_verify_password() -> None:
    hashed = hash_password("secret-pass-99")
    assert hashed != "secret-pass-99"
    assert verify_password("secret-pass-99", hashed)
    assert not verify_password("wrong", hashed)


def test_register_login_me_logout(client: TestClient) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "ops@example.com", "password": "password123", "name": "Ops User"},
    )
    assert register.status_code == 201, register.text
    body = register.json()
    assert body["email"] == "ops@example.com"
    assert body["name"] == "Ops User"
    assert body["role"] == "VIEWER"
    assert "password_hash" not in body
    assert "id" in body

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ops@example.com", "password": "password123"},
    )
    assert login.status_code == 200, login.text
    token_body = login.json()
    assert token_body["token_type"] == "bearer"
    assert token_body["access_token"]
    assert token_body["user"]["email"] == "ops@example.com"
    token = token_body["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ops@example.com"

    logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200
    assert logout.json()["message"] == "Logged out"


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "password123", "name": "Dup"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    again = client.post("/api/v1/auth/register", json=payload)
    assert again.status_code == 409


def test_login_invalid_credentials(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123", "name": "A"},
    )
    bad = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "wrong-pass"})
    assert bad.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_protected_incidents_require_auth(client: TestClient) -> None:
    assert client.get("/api/v1/incidents").status_code == 401


def test_protected_incidents_with_token(client: TestClient) -> None:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "tech@example.com", "password": "password123", "name": "Tech"},
    )
    assert reg.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tech@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    response = client.get("/api/v1/incidents", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_oauth_stubs(client: TestClient) -> None:
    start = client.get("/api/v1/auth/oauth/github")
    assert start.status_code == 501
    callback = client.get("/api/v1/auth/oauth/github/callback")
    assert callback.status_code == 501


def test_first_user_can_bootstrap_admin(client: TestClient) -> None:
    admin = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "password123",
            "name": "Admin",
            "role": "ADMIN",
        },
    )
    assert admin.status_code == 201
    assert admin.json()["role"] == "ADMIN"

    viewer_attempt = client.post(
        "/api/v1/auth/register",
        json={
            "email": "second@example.com",
            "password": "password123",
            "name": "Second",
            "role": "ADMIN",
        },
    )
    assert viewer_attempt.status_code == 201
    assert viewer_attempt.json()["role"] == "VIEWER"


def test_require_roles_helper(db_session: Session) -> None:
    from app.core.security import require_roles

    user = User(
        email="rbac@example.com",
        password_hash=hash_password("password123"),
        name="RBAC",
        role=UserRole.VIEWER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    dependency = require_roles(UserRole.ADMIN, UserRole.TECHNICIAN)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        dependency(user)
    assert exc.value.status_code == 403

    user.role = UserRole.TECHNICIAN
    assert dependency(user) is user


def test_jwt_contains_role(db_session: Session) -> None:
    token = create_access_token(subject="00000000-0000-0000-0000-000000000001", role=UserRole.TECHNICIAN)
    import jwt
    from app.core.config import settings

    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["role"] == "TECHNICIAN"
