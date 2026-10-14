# AI-assisted development decision cases

Three substantive decisions made while building ShareList, each verified rather
than taken on faith.

## 1. Budget boundary semantics (requirements analysis — Claude Code)

- **Problem**: the homework requires edge cases in the acceptance criteria. For
  a budget limit, is a total exactly equal to the limit allowed, or rejected?
- **Tool / context**: Claude Code, during drafting of `SPECIFICATION.md`'s
  acceptance criteria. Instruction given: "treat the budget limit as the
  acceptance criteria's edge case — decide and document whether the boundary
  itself is inside or outside the allowed range."
- **AI's suggestion**: make the boundary inclusive (`total <= budget_limit`
  allowed), since "limit" more naturally reads as "up to and including" in a
  budgeting context, and reject only strictly-over totals.
- **Decision and reasoning**: accepted as-is. It matches how a shopper reads
  "budget limit," and gives a clean, unambiguous edge case to test (the
  alternative, exclusive boundary, would make the limit itself unreachable,
  which is a less natural rule).
- **Verification evidence**: `tests/test_budget_rule.py::test_add_item_exact_budget_boundary_allowed`
  (passes against `assert_within_budget`'s `>` check in
  `backend/app/services/budget.py`); also the deliberately-introduced `>=`
  fault in `tests/faulty_examples/budget_check_faulty.py` makes exactly this
  test fail, which is used as the required faulty-vs-fixed test pair (see
  `tests/results/budget_boundary_FAULTY_run.txt` vs `..._FIXED_run.txt`).

## 2. Role model: enum vs. per-action ACL (implementation — Claude Code)

- **Problem**: how to represent collaborator permissions — a two-value role
  (`editor`/`viewer`) or a more general per-action permission list.
- **Tool / context**: Claude Code, during data-model design. Instruction:
  "design the simplest permission model that still lets AC7/AC8 be expressed
  and tested unambiguously."
- **AI's suggestion**: a `Role` enum (`editor`, `viewer`) on `ListMembership`,
  with the owner having no membership row at all (ownership comes from
  `ShoppingList.owner_id`), checked via two small helper functions
  (`require_owner`, `require_editor_or_owner`) in `services/permissions.py`.
- **Decision and reasoning**: accepted. A general per-action ACL would be
  over-engineered for two roles and three permission levels, and would be
  harder to explain correctly at the individual defence. The enum keeps the
  whole rule in one readable file.
- **Verification evidence**: `tests/test_permissions.py` (non-member → 403,
  viewer → 403 on edit / 200 on bought-toggle) and
  `tests/test_lists.py::test_only_owner_can_patch_budget_or_manage_collaborators`.

## 3. Auth approach: opaque DB token vs. JWT (implementation/testing — Claude Code)

- **Problem**: how to authenticate API requests without adding heavyweight
  dependencies that would be hard to explain at defence.
- **Tool / context**: Claude Code, while building `backend/app/auth.py`.
  Instruction: "pick the simplest auth mechanism that's still realistic and
  fully explainable in a few sentences."
- **AI's suggestion**: an opaque random token (`secrets.token_urlsafe(32)`)
  stored in an `auth_tokens` DB table mapping token → user, checked on every
  request via a FastAPI dependency — instead of a signed JWT.
- **Decision and reasoning**: accepted over JWT. JWT would add a signing-key
  management concern and a `python-jose`/similar dependency with no benefit
  for a single-server app with no horizontal scaling need; the DB-token
  approach is trivial to reason about and revoke (just delete the row), which
  matters for the "explain your own code" part of the defence.
- **Verification evidence**: `tests/test_auth.py::test_login_wrong_password_rejected`
  and the 401/403 paths exercised throughout `tests/test_permissions.py`,
  which depend on `get_current_user` correctly resolving (or rejecting) the
  bearer token.
