import uuid


def auth_headers(client):
    email = f"{uuid.uuid4().hex}@test.dev"
    client.post("/api/auth/register", json={"email": email, "password": "pw", "username": "u"})
    r = client.post("/api/auth/login", json={"email": email, "password": "pw"})
    token = r.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_exercise_crud(client):
    h = auth_headers(client)
    r = client.post("/api/exercise-types", json={"name": "Rowerek"}, headers=h)
    assert r.status_code in (200, 201)
    ex_id = r.get_json()["id"]

    r = client.get("/api/exercise-types", headers=h)
    assert any(x["id"] == ex_id for x in r.get_json())

    r = client.put(f"/api/exercise-types/{ex_id}", json={"name": "Rower"}, headers=h)
    assert r.status_code == 200
    assert r.get_json()["name"] == "Rower"

    r = client.delete(f"/api/exercise-types/{ex_id}", headers=h)
    assert r.status_code in (200, 204)


def test_list_unauthorized(client):
    r = client.get("/api/exercise-types")
    assert r.status_code in (401, 422)


def test_create_validation(client):
    h = auth_headers(client)
    r = client.post("/api/exercise-types", json={}, headers=h)
    assert r.status_code in (400, 422)


def test_duplicate_name_returns_400(client):
    h = auth_headers(client)
    client.post("/api/exercise-types", json={"name": "Bieg"}, headers=h)
    r = client.post("/api/exercise-types", json={"name": "Bieg"}, headers=h)
    assert r.status_code == 400


def test_get_nonexisting_returns_404_or_405(client):
    h = auth_headers(client)
    r = client.get("/api/exercise-types/999999", headers=h)
    assert r.status_code in (404, 405)
