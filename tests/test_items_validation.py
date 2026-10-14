from conftest import register_and_login


def test_invalid_quantity_and_price_rejected(client):
    """AC6 (invalid input): non-positive quantity, negative price, or blank name are rejected
    with 422 and never create an item row."""
    headers = register_and_login(client, "validationuser1")
    list_id = client.post("/lists", json={"name": "List"}, headers=headers).json()["id"]

    bad_quantity = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Thing", "quantity": 0, "unit_price": 5},
        headers=headers,
    )
    assert bad_quantity.status_code == 422

    bad_price = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Thing", "quantity": 1, "unit_price": -1},
        headers=headers,
    )
    assert bad_price.status_code == 422

    bad_name = client.post(
        f"/lists/{list_id}/items",
        json={"name": "", "quantity": 1, "unit_price": 5},
        headers=headers,
    )
    assert bad_name.status_code == 422

    items = client.get(f"/lists/{list_id}", headers=headers).json()["items"]
    assert items == []
