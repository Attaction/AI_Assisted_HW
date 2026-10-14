from conftest import register_and_login


def test_add_item_within_budget_normal(client):
    """AC3 (normal): adding an item within budget succeeds and the total updates."""
    headers = register_and_login(client, "budgetuser1")
    list_id = client.post(
        "/lists", json={"name": "Groceries", "budget_limit": 2000}, headers=headers
    ).json()["id"]

    resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Rice", "quantity": 2, "unit_price": 1000},
        headers=headers,
    )
    assert resp.status_code == 201

    total = client.get(f"/lists/{list_id}", headers=headers).json()["total"]
    assert float(total) == 2000


def test_add_item_exact_budget_boundary_allowed(client):
    """AC4 (edge): a projected total exactly equal to budget_limit is allowed (inclusive boundary)."""
    headers = register_and_login(client, "budgetuser2")
    list_id = client.post(
        "/lists", json={"name": "Party", "budget_limit": 100}, headers=headers
    ).json()["id"]

    resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Cups", "quantity": 10, "unit_price": 10},
        headers=headers,
    )
    assert resp.status_code == 201
    assert float(client.get(f"/lists/{list_id}", headers=headers).json()["total"]) == 100


def test_add_item_over_budget_rejected(client):
    """AC4 (edge): an item pushing the total one unit past budget_limit is rejected with 409,
    and the list total is left unchanged."""
    headers = register_and_login(client, "budgetuser3")
    list_id = client.post(
        "/lists", json={"name": "Party", "budget_limit": 100}, headers=headers
    ).json()["id"]

    client.post(
        f"/lists/{list_id}/items",
        json={"name": "Cups", "quantity": 10, "unit_price": 10},
        headers=headers,
    )

    resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Napkin", "quantity": 1, "unit_price": 1},
        headers=headers,
    )
    assert resp.status_code == 409
    assert float(client.get(f"/lists/{list_id}", headers=headers).json()["total"]) == 100


def test_zero_budget_blocks_any_priced_item(client):
    """AC5 (edge): budget_limit=0 rejects any item with a positive price."""
    headers = register_and_login(client, "budgetuser4")
    list_id = client.post(
        "/lists", json={"name": "Freebies", "budget_limit": 0}, headers=headers
    ).json()["id"]

    resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Candle", "quantity": 1, "unit_price": 0.01},
        headers=headers,
    )
    assert resp.status_code == 409

    free_resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Flyer", "quantity": 1, "unit_price": 0},
        headers=headers,
    )
    assert free_resp.status_code == 201


def test_null_budget_allows_any_total(client):
    """AC5 (edge): budget_limit=null (unset) never triggers a 409, regardless of price."""
    headers = register_and_login(client, "budgetuser5")
    list_id = client.post("/lists", json={"name": "Unlimited"}, headers=headers).json()["id"]

    resp = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Yacht", "quantity": 1, "unit_price": 999999.99},
        headers=headers,
    )
    assert resp.status_code == 201
