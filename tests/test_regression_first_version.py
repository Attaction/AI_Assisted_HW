from conftest import register_and_login

"""Frozen end-to-end regression test, captured at the 'first working version' milestone.

Re-run this file unchanged after implementing the milestone-3 change request to prove
the existing core workflow (and the data it produces) still behaves the same way,
except where the change request explicitly says otherwise.
"""


def test_core_workflow_end_to_end(client):
    owner_headers = register_and_login(client, "regowner")
    collab_headers = register_and_login(client, "regcollab")

    list_id = client.post(
        "/lists", json={"name": "Weekly Groceries", "budget_limit": 50}, headers=owner_headers
    ).json()["id"]

    client.post(
        f"/lists/{list_id}/collaborators",
        json={"username": "regcollab", "role": "editor"},
        headers=owner_headers,
    )

    item = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Bread", "quantity": 2, "unit_price": 10},
        headers=collab_headers,
    )
    assert item.status_code == 201

    over_budget = client.post(
        f"/lists/{list_id}/items",
        json={"name": "Steak", "quantity": 1, "unit_price": 100},
        headers=collab_headers,
    )
    assert over_budget.status_code == 409

    toggle = client.patch(
        f"/lists/{list_id}/items/{item.json()['id']}",
        json={"is_bought": True},
        headers=collab_headers,
    )
    assert toggle.status_code == 200

    final_list = client.get(f"/lists/{list_id}", headers=owner_headers).json()
    assert float(final_list["total"]) == 20
    assert len(final_list["items"]) == 1
    assert final_list["items"][0]["is_bought"] is True
