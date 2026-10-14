# ShareList

Collaborative shopping-list app built for the BME "AI-Assisted Software
Development" homework. See `SPECIFICATION.md` for the full specification and
acceptance criteria.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv\Scripts\activate.bat on cmd
pip install -r requirements.txt
```

## Run

```bash
uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the web UI, or `http://127.0.0.1:8000/docs`
for the interactive API docs.

## Running tests

```bash
pytest tests/ -v
```

All 15 tests should pass. To reproduce the required faulty-vs-fixed
demonstration for the budget-boundary acceptance criterion (AC4):

```bash
# 1. Correct version (shipped) — passes:
pytest tests/test_budget_rule.py::test_add_item_exact_budget_boundary_allowed -v

# 2. Swap services/budget.py's `>` for `>=` (see tests/faulty_examples/budget_check_faulty.py
#    for the exact faulty line), then re-run the same test — it fails. Revert afterward.
```

Captured runs: `tests/results/budget_boundary_FIXED_run.txt` (PASSED) and
`tests/results/budget_boundary_FAULTY_run.txt` (FAILED). Details in
`tests/faulty_examples/README.md`.

## Project structure

```
backend/app/        FastAPI app: models, schemas, auth, routers, business-rule services
frontend/            Plain HTML/JS/CSS UI (no build step), served by FastAPI
tests/               pytest suite, one file per concern, mapped to acceptance criteria
docs/                AI decision log and two-tool comparison
.claude/commands/    custom Claude Code command for scaffolding new AC-mapped tests
```

## AI-Assisted Development

AI tools used: **Claude Code** (primary — requirements analysis, implementation,
testing) and **Gemini** (second-opinion implementation for the two-tool
comparison below). See `AGENTS.md` for the conventions given to AI assistants
working in this repo, and `.claude/commands/add-ac-test.md` for a custom
command that scaffolds new acceptance-criterion-mapped tests.

Three documented decision cases (problem, tool, AI's suggestion, decision +
reasoning, verification evidence) are in **[docs/ai_decisions.md](docs/ai_decisions.md)**:

1. Budget boundary semantics (inclusive vs. exclusive limit) — requirements analysis.
2. Role model: enum vs. per-action ACL — implementation.
3. Auth approach: opaque DB token vs. JWT — implementation/testing.

One feature (`assert_within_budget`) was implemented independently with two
AI tools and compared — see **[docs/two_tool_comparison.md](docs/two_tool_comparison.md)**
(Gemini half to be filled in by actually running Gemini — not simulated).
