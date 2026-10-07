import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import User, UserSession


client = TestClient(app)


def test_register_login_logout_flow() -> None:
    email = f"user-{uuid4()}@example.com"

    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    assert register_response.status_code == 201
    payload = register_response.json()
    assert payload["user"]["email"] == email
    assert payload["user"]["display_name"] == email.split("@", 1)[0]
    assert payload["user"]["role"] == "regular"

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    assert token
    assert login_response.json()["expires_at"]

    with SessionLocal() as db:
        auth_session = db.query(UserSession).filter(UserSession.user_id == payload["user"]["id"]).one()
        assert auth_session.token_hash != token

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_response.status_code == 200

    second_me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_me_response.status_code == 401


def test_register_rejects_duplicate_email() -> None:
    email = f"dup-{uuid4()}@example.com"
    first = client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    assert second.status_code == 409


def test_registration_cannot_assign_elevated_roles() -> None:
    for role in ("chef", "admin"):
        response = client.post(
            "/api/auth/register",
            json={"email": f"{role}-{uuid4()}@example.com", "password": "Password123!", "role": role},
        )
        assert response.status_code == 422


def test_registration_accepts_display_name() -> None:
    email = f"profile-{uuid4()}@example.com"
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!", "display_name": "Home Cook"},
    )
    assert response.status_code == 201
    assert response.json()["user"]["display_name"] == "Home Cook"


def test_password_is_argon2_hashed_at_rest() -> None:
    email = f"hash-{uuid4()}@example.com"
    password = "Password123!"
    response = client.post("/api/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).one()
        assert user.password_hash.startswith("$argon2id$")
        assert user.password_hash != password


def test_login_rejects_invalid_credentials() -> None:
    email = f"invalid-{uuid4()}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "Password123!"})

    wrong_password = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword123!"})
    unknown_email = client.post(
        "/api/auth/login", json={"email": f"missing-{uuid4()}@example.com", "password": "Password123!"}
    )
    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401


def test_protected_endpoint_rejects_missing_and_body_tokens() -> None:
    missing = client.get("/api/auth/me")
    body_token = client.request("GET", "/api/auth/me", json={"token": "not-a-session"})
    assert missing.status_code == 401
    assert body_token.status_code == 401


def test_expired_session_is_rejected() -> None:
    email = f"expired-{uuid4()}@example.com"
    register_response = client.post("/api/auth/register", json={"email": email, "password": "Password123!"})
    user_id = register_response.json()["user"]["id"]
    login_response = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_response.json()["token"]

    with SessionLocal() as db:
        auth_session = db.query(UserSession).filter(UserSession.user_id == user_id).one()
        auth_session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
