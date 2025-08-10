def auth_headers(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "u@x.y", "password": "pw"},
    )
    print("REGISTER:", resp.status_code, resp.get_json())
    assert resp.status_code in (200, 201), (
        f"REGISTER FAIL: {resp.status_code} "
        f"{resp.get_data(as_text=True)}"
    )

    resp = client.post(
        "/api/auth/login",
        json={"email": "u@x.y", "password": "pw"},
    )
    print("LOGIN:", resp.status_code, resp.get_json())
    assert resp.status_code == 200, (
        f"LOGIN FAIL: {resp.status_code} "
        f"{resp.get_data(as_text=True)}"
    )

    data = resp.get_json()
    assert data and "access_token" in data, f"NO TOKEN: {data}"
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_exercise_crud(client):
    h = auth_headers(client)

    # create
    r = client.post("/api/exercise-types", json={"name": "Rowerek"}, headers=h)
    assert r.status_code == 201
    ex_id = r.get_json()["id"]

    # list
    r = client.get("/api/exercise-types", headers=h)
    assert any(x["id"] == ex_id for x in r.get_json())

    # delete
    r = client.delete(f"/api/exercise-types/{ex_id}", headers=h)
    assert r.status_code == 204
