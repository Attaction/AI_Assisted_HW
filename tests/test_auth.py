def test_register_creates_user(client):
    """AC1 (normal): registering with valid data returns 201 and never echoes the password."""
    resp = client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_username_rejected(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob1@example.com", "password": "password123"},
    )
    resp = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob2@example.com", "password": "password123"},
    )
    assert resp.status_code == 409


def test_register_short_password_rejected(client):
    """AC6 (invalid input): password under 8 chars is rejected with 422."""
    resp = client.post(
        "/auth/register",
        json={"username": "carl", "email": "carl@example.com", "password": "short"},
    )
    assert resp.status_code == 422


def test_login_wrong_password_rejected(client):
    client.post(
        "/auth/register",
        json={"username": "dana", "email": "dana@example.com", "password": "password123"},
    )
    resp = client.post("/auth/login", json={"username": "dana", "password": "wrongpass"})
    assert resp.status_code == 401


def test_password_stored_hashed_and_salted(client):
    """AC1 (normal): the stored password is hashed+salted, never plaintext, and each user gets a different salt."""
    from backend.app.database import get_db
    from backend.app.models import User

    for name in ("erin", "frank"):
        resp = client.post(
            "/auth/register",
            json={"username": name, "email": f"{name}@example.com", "password": "password123"},
        )
        assert resp.status_code == 201

    db = next(client.app.dependency_overrides[get_db]())
    try:
        erin = db.query(User).filter_by(username="erin").one()
        frank = db.query(User).filter_by(username="frank").one()
    finally:
        db.close()

    assert erin.password_hash != "password123"
    assert "password123" not in erin.password_hash
    assert erin.password_salt
    assert erin.password_salt != frank.password_salt
    # Same password, different salt -> different hash.
    assert erin.password_hash != frank.password_hash
