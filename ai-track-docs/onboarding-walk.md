# Onboarding Prompt — Walk Track

> Paste this file into Copilot Chat at the start of a new walk exercise session.
> It gives Copilot the repo context, workflow rules, and file conventions needed
> to work effectively without repeated explanation.

---

## Repo context

This is **copilot-cli-for-beginners** — a beginner-friendly educational course
teaching GitHub Copilot CLI. It is courseware, not a software product.

**Primary sample app**: `samples/book-app-project/` (Python 3.10+)
- `book_app.py` — CLI entry point
- `books.py` — `Book` dataclass + `BookCollection` (loads/saves `data.json`)
- `utils.py` — UI helpers (`show_books`, `parse_year`, menu, prompts)
- `data.json` — persistent JSON store
- `tests/test_books.py` — pytest suite (5 tests, `books.py` at ≥ 85%)

**Do not touch**: `samples/book-app-buggy/` and `samples/buggy-code/` contain
intentional bugs for debugging exercises — never fix them.

---

## Walk workflow rules

1. **One branch per exercise**: `walk/ex-<N>-<slug>` (e.g. `walk/ex-04-onboarding-docs`)
2. **Prompt structure** (from `.copilot-track/walk/prompt-exercise.md`):
   - **Mini Prompt** — one-sentence goal
   - **Steps** — ordered, actionable steps to follow
   - **Acceptance** — pass/fail checkpoints to verify before declaring done
   - **Troubleshooting** — hints for ambiguity
3. **After every exercise**:
   - Generate a filled PR template using `.copilot-track/walk/pr-template.md`
   - Save `ai-track-docs/ex-<N>-<summary>.md` with steps run, acceptance results, and PR template
   - Commit the context file alongside the exercise changes

---

## PR template format

```
Title: GHCP -- Walk: <ex#> <name>

Summary / Plan / Files touched
Evidence: test command + output + coverage %
Risk & Rollback
Review Focus (runnable verification step)
Track: Level: Walk / Exercise: <ex#>
```

Full template: `.copilot-track/walk/pr-template.md`

---

## Test and coverage commands

```bash
cd samples/book-app-project
.venv/bin/pytest          # runs tests + coverage (configured in pyproject.toml)
npm run validate:arch     # validates ai-track-docs/architecture.md paths (from repo root)
```

**Coverage targets**: `books.py` ≥ 85%; overall total will be lower (CLI/UI modules not unit-tested by design).

---

## Key conventions

- File names: kebab-case (`ex-04-onboarding-docs.md`, not `ex04_onboarding_docs`)
- Exercise context files: `ai-track-docs/ex-<N>-<summary>.md` (N zero-padded, e.g. `04`)
- Architecture doc: `ai-track-docs/architecture.md` — keep Module Map table up to date when adding files
- Coverage section in PRs: always include the `TOTAL` line from `pytest` output

---

## Current exercise log

| # | File | Summary |
|---|---|---|
| 01 | `ai-track-docs/ex-01-architecture-map.md` | Architecture doc + path validation script |
| 02 | `ai-track-docs/ex-02-coverage-reporting.md` | pytest-cov enabled, CONTRIBUTING updated |
| 03 | `ai-track-docs/ex-03-refactor-consolidate-helpers.md` | Consolidated duplicate display/year-parse logic |
| 04 | `ai-track-docs/ex-04-onboarding-docs.md` | CONTRIBUTING Walk section + this onboarding prompt |
| 05 | `ai-track-docs/ex-05-contract-tests.md` | data.json schema contract tests + golden fixture |
| 06 | `ai-track-docs/ex-06-micro-optimization.md` | Hoisted .lower() out of search loops (−29–30%) |
| 07 | `ai-track-docs/ex-07-dependency-upgrade.md` | pip 25.2 → 26.1.1 upgrade |
| 08 | `ai-track-docs/ex-08-secret-scanning.md` | Secret scanner + .gitleaks.toml + SECURITY.md |
| 09 | `ai-track-docs/ex-09-structured-logging.md` | Structured JSON logging hooks on BookCollection |
| 10 | `ai-track-docs/ex-10-ci-evidence-summary.md` | Advisory CI evidence workflow (non-blocking) |
| 11 | `ai-track-docs/ex-11-pr-review-template.md` | Exemplary PR writing: review focus, verification, rollback |
| 12 | `ai-track-docs/ex-12-backlog-epic.md` | Epic + 5 backlog items with acceptance criteria |
| 13 | `ai-track-docs/ex-13-flag-lifecycle.md` | BOOK_APP_STRICT_YEAR flag: lifecycle doc + ON/OFF matrix |
| 14 | `ai-track-docs/ex-14-strict-lint.md` | ruff strict gate on books.py: fix + suppress + CI |

**Future work**: see `ai-track-docs/backlog.md` for 5 scoped items ready to become PRs.
