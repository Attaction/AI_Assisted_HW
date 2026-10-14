# Faulty/fixed pair — budget boundary check

Rubric requirement: keep both a faulty and corrected version of one piece of logic,
plus both test run outputs, showing a test fail on the faulty version and pass on
the corrected one.

- `budget_check_faulty.py` — off-by-one variant of `assert_within_budget` (`>=`
  instead of `>`), incorrectly rejecting the inclusive boundary case (AC4).
- `../../backend/app/services/budget.py` — the actual, correct version shipped in
  the app (`>`).
- `../test_budget_rule.py::test_add_item_exact_budget_boundary_allowed` — the test
  that distinguishes the two.
- `../results/budget_boundary_FAULTY_run.txt` / `budget_boundary_FIXED_run.txt` —
  captured pytest output for each variant (see README.md "Running tests" section
  for the exact commands used to produce these).

This fault was introduced deliberately for the assignment; it was not an actual
defect found during development of this project.
