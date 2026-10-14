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
