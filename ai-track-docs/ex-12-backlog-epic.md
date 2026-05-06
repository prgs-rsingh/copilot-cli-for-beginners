# Exercise 12 — Epic + Backlog: 5 Actionable Items with Acceptance Criteria

## Mini Prompt
Draft an epic with 3-5 issues with acceptance and links; if no tracker access, commit a backlog doc.

---

## Approach

GitHub Issues tracker is not accessible from the agent environment, so the backlog is committed
as `ai-track-docs/backlog.md`. Each item is scoped to one PR and includes acceptance criteria,
linked code paths, and a verification command.

---

## Backlog Items

| # | Item | Type | Priority | Key file(s) |
|---|---|---|---|---|
| 1 | Cover `books.py` error paths → 100% | Test | High | `books.py` lines 31-35, 51, 83-84 |
| 2 | O(1) title lookup dict index | Performance | Medium | `books.py` — `find_book_by_title`, `add_book`, `remove_book` |
| 3 | Automated `BOOK_SCHEMA` drift detection | Contract | Medium | `test_contract.py`, `books.py::Book` |
| 4 | Log rotation + optional file output | Operability | Low-Medium | `logging_config.py` |
| 5 | Blocking `ruff` lint step in CI | CI / Quality | Medium | `pyproject.toml`, `.github/workflows/` |

---

## Dependency Order

```
Item 3 (schema drift)   — no deps  →  can start immediately
Item 4 (log rotation)   — no deps  →  can start immediately
Item 1 (coverage 100%)  — no deps  →  can start immediately
Item 2 (O(1) lookup)    — after Item 1 (coverage baseline secured)
Item 5 (lint CI gate)   — after Item 1 (avoid lint fixes breaking coverage)
```

Suggested order: **3 → 4 → 1 → 2 → 5**

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Reviewed all ex-01→11 context files and current `books.py` coverage gaps (lines 31-35, 51, 83-84) | 5 backlog candidates identified |
| 2 | Risk-ranked candidates: coverage holes (high risk — real failure modes), O(1) lookup (perf), schema drift (silent contract risk), log rotation (operability), lint gate (CI quality) | Priority and order set |
| 3 | Created `ai-track-docs/backlog.md` with epic description, 5 items, acceptance criteria, code path links, dependency graph | Created |
| 4 | Updated `ai-track-docs/onboarding-walk.md` exercise log with ex-12 + backlog reference | Updated |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| 3-5 actionable backlog items | ✅ Pass — 5 items, each scoped to one PR |
| Acceptance criteria included | ✅ Pass — checkboxed acceptance criteria for each item |
| Linked to code paths | ✅ Pass — file paths and line numbers in every item |

---

## Files Changed

| File | Change |
|---|---|
| `ai-track-docs/backlog.md` | Created — epic + 5 backlog items with acceptance criteria and code links |
| `ai-track-docs/onboarding-walk.md` | Added ex-12 to exercise log + backlog reference |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 12 Epic + Backlog — 5 Actionable Items with Acceptance Criteria

## Summary
- Reviewed walk track findings (ex-01→11) and identified 5 improvements warranting future PRs.
- No GitHub Issues access from agent environment → committed `ai-track-docs/backlog.md`.
- Epic: **book-app-project — Quality, Performance, and Operability hardening**
- 5 items, each scoped to one PR, with checkboxed acceptance criteria, code path links,
  verification commands, and a dependency order:
  1. Cover `books.py` error paths → 100% (high priority)
  2. O(1) title lookup dict index (perf)
  3. Automated `BOOK_SCHEMA` drift detection (silent contract risk)
  4. Log rotation + `LOG_FILE` env var (operability)
  5. Blocking `ruff` lint step in CI (quality gate)
- Updated `ai-track-docs/onboarding-walk.md` to include ex-12 and backlog reference.
- Plan: inline — backlog doc only; no code changes.
- Files/paths touched:
  - `ai-track-docs/backlog.md` (new)
  - `ai-track-docs/onboarding-walk.md` (ex-12 added)

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest` → 9 passed (no code changed)
- Coverage: 48% total (books.py 88%) — unchanged

## Risk & Rollback
- Risk: low — doc-only change
- Rollback: revert this commit

## Review Focus
- Read `ai-track-docs/backlog.md` — verify each item is scoped to one PR (not too large)
- Confirm dependency order (3→4→1→2→5) matches the rationale in each item
- Check Item 3 (BOOK_SCHEMA drift) — verify the acceptance criteria would actually catch
  a field rename in `books.py::Book` before a PR merges
- Check Item 5 (lint gate) — confirm the acceptance criteria requires the check to be added
  to branch protection required checks (not just advisory)

## Track
- Level: Walk
- Exercise: 12
```
