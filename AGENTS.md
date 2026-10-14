# Agent conventions — ShareList

Notes for any AI coding assistant (Claude Code, Gemini, etc.) working in this repo.

## Run / test

```
pip install -r requirements.txt
uvicorn backend.app.main:app --reload   # app on http://127.0.0.1:8000
pytest tests/ -v
```

## Conventions

- **Money is always `Decimal`/SQLAlchemy `Numeric`, never `float`.** Float rounding
  breaks the budget-boundary acceptance criterion (AC4).
- **Business rules live only in `backend/app/services/`** (`budget.py`,
  `permissions.py`). Routers call these services and translate their exceptions
  (`errors.py`) to HTTP status codes — they never re-implement a rule inline. This
  keeps the milestone-3 change request traceable to one or two files.
- **Every new rule or endpoint needs a pytest test whose docstring names the
  acceptance criterion it covers** (e.g. `"""AC4 (edge): ..."""`), following the
  existing tests in `tests/`.
- **Do not modify `tests/faulty_examples/`.** Those files are frozen grading
  evidence for the deliberate faulty-vs-fixed test pair (see
  `tests/faulty_examples/README.md`); editing them invalidates that evidence.
- **`tests/test_regression_first_version.py` is frozen** once the first working
  version is recorded — it must keep passing unchanged after the milestone-3
  change request, to prove existing behavior/data is preserved.
