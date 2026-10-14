---
description: Scaffold a new acceptance-criterion-mapped pytest test following this repo's conventions
---

Add a new test for acceptance criterion **$ARGUMENTS** to the ShareList test suite.

Steps:
1. Read `SPECIFICATION.md` to find the exact wording of the acceptance criterion number given.
2. Pick the matching test file under `tests/` by topic (auth → `test_auth.py`, lists/ownership →
   `test_lists.py`, budget rule → `test_budget_rule.py`, invalid input → `test_items_validation.py`,
   roles/authorization → `test_permissions.py`). Create a new file only if none fit.
3. Use the `client` fixture and `register_and_login` helper from `tests/conftest.py` — do not
   duplicate that setup.
4. Write the test function with a docstring starting `"""AC<N> (normal|edge|invalid input|unauthorized): ..."""`
   stating exactly what the acceptance criterion requires, matching the style already used in
   `tests/test_budget_rule.py` and `tests/test_permissions.py`.
5. Run `pytest tests/ -v` and confirm the new test (and the rest of the suite) passes before
   reporting done.
