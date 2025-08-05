import uuid


def test_register_and_login(client):
    email = f"{uuid.uuid4().hex}@test.dev"

    res = client.post(
        "/api/auth/register",
        json={"email": email, "password": "pw", "username": "adam"},
    )
    assert res.status_code == 201

    res = client.post("/api/auth/login", json={"email": email, "password": "pw"})
    assert res.status_code == 200

