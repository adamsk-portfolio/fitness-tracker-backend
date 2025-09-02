import uuid


def test_register_and_login(client):
    email = f"{uuid.uuid4().hex}@test.dev"
    r = client.post(
        "/api/auth/register", json={"email": email, "password": "pw", "username": "adam"}
    )
    assert r.status_code in (200, 201)
    r = client.post("/api/auth/login", json={"email": email, "password": "pw"})
    assert r.status_code == 200
    assert "access_token" in r.get_json()


def test_register_duplicate_email(client):
    email = f"{uuid.uuid4().hex}@test.dev"
    client.post("/api/auth/register", json={"email": email, "password": "pw"})
    r = client.post("/api/auth/register", json={"email": email, "password": "pw"})
    assert r.status_code == 400


def test_login_invalid_credentials(client):
    email = f"{uuid.uuid4().hex}@test.dev"
    client.post("/api/auth/register", json={"email": email, "password": "pw"})
    r = client.post("/api/auth/login", json={"email": email, "password": "bad"})
    assert r.status_code == 401
