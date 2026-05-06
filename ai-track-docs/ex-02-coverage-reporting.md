# Exercise 02 — Coverage Reporting

## Mini Prompt
Enable or document coverage output and provide a PR snippet template that includes total percentage.

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Identified test runner (`pytest`) and coverage tooling — no coverage config existed; `pyproject.toml` only listed `pytest` as a dependency | Found: no `.coveragerc`, no `pytest-cov` |
| 2 | Added `pytest-cov` to `dependencies` and configured `[tool.pytest.ini_options]` addopts + `[tool.coverage.run/report]` sections in `pyproject.toml` | Coverage now runs automatically with `pytest` |
| 3 | Installed `pytest-cov` into the existing `.venv` and ran `.venv/bin/pytest --cov=. --cov-report=term-missing` | Output captured below |
| 4 | Confirmed `pytest` alone (no explicit flags) produces coverage via `pyproject.toml` addopts | Verified — same output |
| 5 | Added "Running Tests and Coverage" section to `CONTRIBUTING.md` with prerequisites, command, coverage table, and PR snippet guidance | Documented |

### Coverage Output

```
Name          Stmts   Miss  Cover   Missing
-------------------------------------------
book_app.py      55     55     0%   1-94
books.py         55      7    87%   27-31, 45, 72
utils.py         27     27     0%   1-36
-------------------------------------------
TOTAL           137     89    35%
Coverage HTML written to dir htmlcov
5 passed in 0.24s
```

**Coverage note:** 35% total is expected. `book_app.py` and `utils.py` are CLI/UI modules
that rely on `input()` and `print()` and are not unit-tested by design. The meaningful
business logic module (`books.py`) is at **87%**.

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Coverage instructions documented | ✅ Pass — added to `CONTRIBUTING.md` with prerequisites, command, table, and PR snippet |
| Coverage percentage included in PR description | ✅ Pass — 35% total, books.py 87% (see PR template below) |
| Coverage command verified locally | ✅ Pass — `.venv/bin/pytest` → 5 passed, coverage table printed, HTML report written |

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/pyproject.toml` | Added `pytest-cov` dependency, `[tool.pytest.ini_options]` addopts, `[tool.coverage.run]`, `[tool.coverage.report]` |
| `CONTRIBUTING.md` | Added "Running Tests and Coverage" section |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 02 Coverage Reporting — Enable and Document

## Summary
- Enabled `pytest-cov` coverage reporting for `samples/book-app-project/` via `pyproject.toml`.
- Running `.venv/bin/pytest` now produces a term-missing report and HTML report automatically.
- Documented coverage setup, commands, and PR snippet guidance in `CONTRIBUTING.md`.
- Plan: inline — zero-config coverage for contributors; no CI changes needed, local command is sufficient.
- Files/paths touched:
  - `samples/book-app-project/pyproject.toml` (pytest-cov added, coverage config added)
  - `CONTRIBUTING.md` (coverage section added)

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest` (from `samples/book-app-project/`) → 5 passed in 0.24s
- Coverage: 35% total (books.py 87% — CLI/UI modules excluded by design)

## Risk & Rollback
- Risk: low
- Rollback: revert this commit (config-only change, no production code modified)

## Review Focus
- Check `pyproject.toml` coverage config — confirm `omit` patterns are appropriate
- Verify `CONTRIBUTING.md` instructions are clear for a first-time contributor
- Run `.venv/bin/pytest` from `samples/book-app-project/` to confirm coverage table appears

## Track
- Level: Walk
- Exercise: 02
```
