# Two-tool comparison: `assert_within_budget` — Claude Code vs. Gemini

Rubric requirement: implement one feature twice with two different AI tools and
evaluate the differences. Chosen feature: the budget-boundary check
(`assert_within_budget`), small and isolated enough to compare meaningfully.

**This file is a template — the Gemini half must be filled in by actually
running Gemini, not simulated.** Claude Code's half is already real (it's the
shipped implementation).

## Shared prompt (paste verbatim into both tools)

> Write a Python function `assert_within_budget_gemini(shopping_list, projected_total)`
> using `decimal.Decimal`. `shopping_list` is a SQLAlchemy `ShoppingList` model
> with a `budget_limit` attribute (a `Numeric` column, may be `None` meaning no
> limit, always allowed). `projected_total` is a `Decimal`. Raise
> `BudgetExceededError` (from `backend.app.errors`) with a message including
> both values if `projected_total` exceeds `budget_limit`. A `projected_total`
> exactly equal to `budget_limit` must be **allowed** (inclusive boundary).
> Never use `float` for money. Return only the function, with imports.

Note: the signature matches the shipped function (takes the model, not a bare
`budget_limit`) so both tools solve the same problem. Run it in a fresh
workspace with no view of `backend/app/services/budget.py`.

## Claude Code's implementation (shipped)

`backend/app/services/budget.py`:

```python
def assert_within_budget(shopping_list: ShoppingList, projected_total: Decimal) -> None:
    if shopping_list.budget_limit is None:
        return
    if projected_total > Decimal(shopping_list.budget_limit):
        raise BudgetExceededError(
            f"Projected total {projected_total} exceeds budget limit {shopping_list.budget_limit}"
        )
```

Passes: all of `tests/test_budget_rule.py` (5/5), including the inclusive
boundary case.

## Gemini's implementation — TODO, fill in after running Gemini

Paste into `docs/gemini_variant/budget_gemini.py`, then fill in below:

```python
# TODO: paste Gemini's function here
```

Test result when swapped in for the shipped function (run
`pytest tests/test_budget_rule.py -v` with the swap in place, same method used
for the faulty/fixed pair): TODO — record pass/fail per test.

## Evaluation — TODO after running Gemini

Compare on:
- **Boundary correctness** — did it get the inclusive boundary right on the
  first attempt, or did the prompt need a follow-up correction?
- **Decimal handling** — did it correctly avoid `float`, or need a fix?
- **Error message quality** — does the raised error include both values
  clearly?
- **Readability** — which version would be easier to explain cold at the
  defence?

Write 3-5 sentences here with the actual outcome once both tools have been run.
