def auth_headers(client):
    client.post("/auth/register", json={"email": "u@x.y", "password": "pw"})
    token = client.post(
        "/auth/login",
        json={"email": "u@x.y", "password": "pw"}
    ).get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_exercise_crud(client):
    h = auth_headers(client)

    # create
    r = client.post("/exercise-types", json={"name": "Rowerek"}, headers=h)
    assert r.status_code == 201
    ex_id = r.get_json()["id"]

    # list
    r = client.get("/exercise-types", headers=h)
    assert any(x["id"] == ex_id for x in r.get_json())

    # delete
    r = client.delete(f"/exercise-types/{ex_id}", headers=h)
    assert r.status_code == 204
