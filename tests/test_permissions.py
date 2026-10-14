from conftest import register_and_login


def test_non_member_forbidden(client):
    """AC7 (unauthorized): a user who is neither owner nor collaborator gets 403."""
    owner_headers = register_and_login(client, "permowner1")
    outsider_headers = register_and_login(client, "outsider1")

    list_id = client.post("/lists", json={"name": "Private"}, headers=owner_headers).json()["id"]

    get_resp = client.get(f"/lists/{list_id}", headers=outsider_headers)
    assert get_resp.status_code == 403

    add_resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Snoop", "quantity": 1, "unit_price": 1},
        headers=outsider_headers,
    )
    assert add_resp.status_code == 403


def test_viewer_cannot_edit_but_can_mark_bought(client):
    """AC7 (unauthorized): a viewer collaborator gets 403 on add/edit/delete but 200 on
    toggling is_bought."""
    owner_headers = register_and_login(client, "permowner2")
    viewer_headers = register_and_login(client, "viewer2")

    list_id = client.post("/lists", json={"name": "Shared"}, headers=owner_headers).json()["id"]
    client.post(
        f"/lists/{list_id}/collaborators",
        json={"username": "viewer2", "role": "viewer"},
        headers=owner_headers,
    )
    item = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Milk", "quantity": 1, "unit_price": 2},
        headers=owner_headers,
    ).json()

    add_resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Bread", "quantity": 1, "unit_price": 2},
        headers=viewer_headers,
    )
    assert add_resp.status_code == 403

    edit_resp = client.patch(
        f"/lists/{list_id}/items/{item['id']}",
        json={"name": "Renamed"},
        headers=viewer_headers,
    )
    assert edit_resp.status_code == 403

    delete_resp = client.delete(
        f"/lists/{list_id}/items/{item['id']}", headers=viewer_headers
    )
    assert delete_resp.status_code == 403

    bought_resp = client.patch(
        f"/lists/{list_id}/items/{item['id']}",
        json={"is_bought": True},
        headers=viewer_headers,
    )
    assert bought_resp.status_code == 200
    assert bought_resp.json()["is_bought"] is True
