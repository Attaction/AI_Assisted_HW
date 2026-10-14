# ShareList — Specification

## Goal

ShareList is a collaborative shopping-list web app. A user creates lists,
optionally sets a budget limit, and invites other users as collaborators with
an editor or viewer role. The server enforces a budget rule and a permission
rule so the app has real, testable business logic beyond basic CRUD.

## Roles

- **Owner** — creator of a list. Can rename it, set/change its budget, and
  manage collaborators.
- **Collaborator (editor)** — can add, edit, and delete items on a shared list.
- **Collaborator (viewer)** — can only mark items as bought/unbought.
- **Non-member** — any other registered user; has no access to a list.

## Main scenarios

1. Register and log in with username/email/password.
2. Create a list, optionally with a budget limit.
3. Add items (name, quantity, unit price) to a list, subject to the budget rule.
4. Invite another user as an editor or viewer collaborator.
5. Collaborators work on a shared list according to their role.
6. Owner adjusts the budget or removes a collaborator.

## Acceptance criteria

1. **Normal — register**: valid unique username/email + password (≥8 chars)
   → `201`, password never returned, stored hashed+salted.
2. **Normal — create list**: authenticated `POST /lists` → `201`, caller
   becomes owner, list starts empty with total `0`.
3. **Normal — add item within budget** → `201`, list total updates correctly.
4. **Edge — budget boundary**: an item landing exactly on `budget_limit` is
   allowed (`201`); the next item pushing the total one unit past it is
   rejected (`409`), and the total stays unchanged.
5. **Edge — zero vs. unset budget**: `budget_limit=0` rejects any item with a
   positive price (`409`); `budget_limit=null` accepts items of any price.
6. **Invalid input**: non-positive quantity, negative price, or blank name →
   `422`, no item created.
7. **Unauthorized**: a non-member gets `403` on any access to a list; a viewer
   gets `403` on add/edit/delete but `200` on toggling bought.
8. **Ownership-only**: only the owner may change a list's name/budget or
   manage its collaborators; others get `403`.

## Business rules

- **Budget rule**: a list's running total (`sum(quantity × unit_price)` over
  all items, bought or not) may never exceed its `budget_limit` if one is set.
- **Permission rule**: owner manages budget/name/membership; editors add/
  edit/delete items; viewers only toggle the bought flag.

## Uncertainties and chosen interpretation

- Whether the budget counts already-bought items: **yes** — the budget tracks
  total planned spend, not just what's left to buy.
- Whether the budget boundary is inclusive or exclusive at the limit itself:
  **inclusive** — a total exactly equal to the limit is allowed.
- Whether viewers can interact with items at all: **yes, bought-toggle only**
  — lets a viewer participate (e.g. while actually shopping) without granting
  edit rights.

Business-rule logic is isolated in `backend/app/services/budget.py` and
`backend/app/services/permissions.py` so a later change request to either
rule can be implemented and traced without restructuring the app.
