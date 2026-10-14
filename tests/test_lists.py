from conftest import register_and_login


def test_create_list_normal(client):
    """AC2 (normal): creating a list makes the caller owner with an empty, zero-total list."""
    headers = register_and_login(client, "owner1")
    resp = client.post("/lists", json={"name": "Groceries", "budget_limit": 100}, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["items"] == []
    assert float(body["total"]) == 0

    get_resp = client.get(f"/lists/{body['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["owner_id"] == body["owner_id"]


def test_only_owner_can_patch_budget_or_manage_collaborators(client):
    """AC8: non-owners get 403 on PATCH /lists/{id} and on collaborator management."""
    owner_headers = register_and_login(client, "owner2")
    other_headers = register_and_login(client, "stranger2")

    create_resp = client.post("/lists", json={"name": "Trip"}, headers=owner_headers)
    list_id = create_resp.json()["id"]

    patch_resp = client.patch(f"/lists/{list_id}", json={"name": "Hacked"}, headers=other_headers)
    assert patch_resp.status_code == 403

    add_collab_resp = client.post(
        f"/lists/{list_id}/collaborators",
        json={"username": "stranger2", "role": "editor"},
        headers=other_headers,
    )
    assert add_collab_resp.status_code == 403

    owner_patch = client.patch(f"/lists/{list_id}", json={"name": "Renamed"}, headers=owner_headers)
    assert owner_patch.status_code == 200
    assert owner_patch.json()["name"] == "Renamed"

    owner_add = client.post(
        f"/lists/{list_id}/collaborators",
        json={"username": "stranger2", "role": "editor"},
        headers=owner_headers,
    )
    assert owner_add.status_code == 201

    collabs = client.get(f"/lists/{list_id}/collaborators", headers=owner_headers)
    usernames = [c["username"] for c in collabs.json()]
    assert "stranger2" in usernames
