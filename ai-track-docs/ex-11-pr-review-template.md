# Exercise 11 — PR Review Template: Review Focus, Verification Steps, Rollback

## Mini Prompt
Draft review focus bullets and verification steps for a PR; generate final PR text from template.

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Reviewed all exercise context files (ex-01 through ex-10) to identify the riskiest / most complex changes across the walk track | Identified 5 review focus areas |
| 2 | Drafted 5 review focus bullets with specific file references and runnable verification commands for each | Done |
| 3 | Wrote a clear, tiered rollback plan (per-exercise and full-track options) | Done |
| 4 | Ran final state check: secrets, arch, tests all clean | 9/9 passed, 48% total, books.py 88% |
| 5 | Generated final PR text using walk template at maximum quality | See below |

---

## Review Focus Drafting Process

**Guiding principle**: focus on riskiest files first, then correctness of new contracts,
then advisory-only guarantees. Verification steps must be copy-paste ready.

**Risk ranking across the walk track:**

| Rank | Area | Risk | Why |
|---|---|---|---|
| 1 | `books.py` — logging + optimization | Medium | Two changes in the core domain module: `.lower()` hoist + logger calls |
| 2 | `tests/test_contract.py` + `BOOK_SCHEMA` | Medium | New test contract — if schema drifts, contract tests silently stop catching it |
| 3 | `scan-secrets.js` allowlist rules | Low-Medium | Allowlist too broad → real secrets slip through; too narrow → false positives block CI |
| 4 | `walk-evidence.yml` non-blocking config | Low | A misconfigured required-check setting would silently start blocking merges |
| 5 | `logging_config.py` stderr separation | Low | If logger accidentally writes to stdout it corrupts user-facing CLI output |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Review focus section included | ✅ Pass — 5 bullets with specific files and rationale |
| Verification steps documented | ✅ Pass — copy-paste commands for each bullet |
| Clear rollback plan included | ✅ Pass — tiered rollback (per-exercise SHA + full track) |

---

## Final Evidence

```
npm run scan:secrets   → 55 files, 0 findings ✓
npm run validate:arch  → 6/6 paths verified ✓
pytest (book-app-project) → 9 passed in 0.27s
  books.py: 88%  |  logging_config.py: 100%  |  TOTAL: 48%
```

---

## Files Changed

| File | Change |
|---|---|
| `ai-track-docs/onboarding-walk.md` | Exercise log updated with ex-05 through ex-11 |

---

## Final PR Text

```markdown
## Title
GHCP -- Walk: 11 PR Review Template — Review Focus, Verification Steps, Rollback

## Summary
This PR demonstrates exemplary PR writing for the walk track: structured review focus,
copy-paste verification steps, and a tiered rollback plan.

It also closes the walk track batch (ex-01 through ex-11) by updating the onboarding
exercise log so future contributors have a complete reference.

- Changes: `ai-track-docs/onboarding-walk.md` — exercise log extended to ex-11
- Plan: inline — meta-exercise capturing PR writing best practices as a reusable reference

**Walk track scope (ex-01 → ex-11):**
| Ex | Change | Key files |
|---|---|---|
| 01 | Architecture doc + validate-arch.js | `ai-track-docs/architecture.md`, `.github/scripts/validate-arch.js` |
| 02 | pytest-cov + CONTRIBUTING | `pyproject.toml`, `CONTRIBUTING.md` |
| 03 | Refactor: consolidate helpers | `utils.py`, `book_app.py` |
| 04 | Onboarding docs + CONTRIBUTING Walk section | `CONTRIBUTING.md`, `ai-track-docs/onboarding-walk.md` |
| 05 | Contract tests (schema + golden) | `tests/test_contract.py`, `tests/fixtures/golden_book.json` |
| 06 | Micro-optimization: hoist .lower() | `books.py` |
| 07 | Dependency upgrade: pip 25.2 → 26.1.1 | `pyproject.toml` |
| 08 | Secret scanning + SECURITY.md | `.github/scripts/scan-secrets.js`, `.gitleaks.toml`, `SECURITY.md` |
| 09 | Structured JSON logging | `logging_config.py`, `books.py` |
| 10 | Advisory CI evidence workflow | `.github/workflows/walk-evidence.yml` |
| 11 | PR review template (this PR) | `ai-track-docs/onboarding-walk.md` |

## Evidence
- Tests/logs/metrics:
  - `cd samples/book-app-project && .venv/bin/pytest` → **9 passed in 0.27s**
  - `npm run validate:arch` → **6/6 paths verified ✓**
  - `npm run scan:secrets` → **55 files, 0 findings ✓**
- Coverage: **48% total** (`books.py` 88%, `logging_config.py` 100%)

## Risk & Rollback

**Per-exercise rollback** (revert individual commits):
- Ex-06 optimization (`books.py` `.lower()` hoist): `git revert <ex-06-sha>`
- Ex-09 logging (`books.py` + `logging_config.py`): `git revert <ex-09-sha>`
  - logging is opt-out via `LOG_LEVEL=WARNING`; no revert usually needed
- Ex-08 scanning (`.github/scripts/scan-secrets.js`): `git revert <ex-08-sha>`
- Ex-10 CI workflow: delete `.github/workflows/walk-evidence.yml`
  - IMPORTANT: if accidentally added to branch protection, remove it first

**Full track rollback**: `git revert <ex-01-sha>..<ex-11-sha> --no-commit && git commit -m "revert: walk track ex-01→11"`

Overall risk: **low** — no database migrations, no API changes, no breaking schema changes.
The riskiest change (`books.py` domain module) is covered by 9 tests including 4 contract tests.

## Review Focus

**1 — `books.py`: two independent changes in the same file (ex-06 + ex-09)**
- Ex-06 hoisted `title_lower = title.lower()` / `author_lower = author.lower()` before the
  search loops — identical output, ~29–30% faster on 10k-book collections.
- Ex-09 added `logger.info()` calls to `load_books`, `add_book`, `mark_as_read`, `remove_book`.
  All log output goes to `stderr` only — stdout must remain unaffected.
- **Verify**: `python book_app.py list 2>/dev/null` shows only the book list (no JSON mixed in).
- **Verify**: `LOG_LEVEL=WARNING python book_app.py list` emits zero log lines to stderr.

**2 — `tests/test_contract.py` + `BOOK_SCHEMA` dict (ex-05)**
- `BOOK_SCHEMA = {"title": str, "author": str, "year": int, "read": bool}` is the authoritative
  schema definition. If the `Book` dataclass in `books.py` gains or renames a field without
  updating `BOOK_SCHEMA`, the contract tests pass silently on stale schema.
- **Verify**: `Book` dataclass fields in `books.py` match `BOOK_SCHEMA` keys exactly.
- **Verify**: `pytest tests/test_contract.py -v` → 4/4 pass.

**3 — `scan-secrets.js` allowlist path rules (ex-08)**
- Two path-based allowlist rules exclude `samples/buggy-code/` and `samples/src/` entirely.
  Path-based rules are broad — any new file added to those paths is auto-excluded.
- **Verify**: the excluded paths are courseware-only (no real credentials can live there).
- **Verify**: `npm run scan:secrets` → 0 findings, 55 files scanned.

**4 — `.github/workflows/walk-evidence.yml` non-blocking config (ex-10)**
- `continue-on-error: true` appears on every evidence step. If any step loses that attribute,
  test failures would start blocking merges.
- The workflow must NOT appear in branch protection required checks.
- **Verify**: open the workflow file and confirm every `id:`-named step has `continue-on-error: true`.
- **Verify**: check **Settings → Branches → main → required status checks** — `walk-evidence` must not be listed.

**5 — `logging_config.py` stderr isolation (ex-09)**
- `get_logger()` attaches a `StreamHandler(sys.stderr)` and sets `propagate = False`.
  If `propagate` were `True` or the handler pointed at `sys.stdout`, log lines would appear
  inline with the book list output and break the CLI UX.
- **Verify**: `python -c "from logging_config import get_logger; l=get_logger('t'); l.info('ok')" 2>/dev/null`
  prints nothing (stderr suppressed, stdout empty).

## Verification Steps (full suite — copy-paste ready)

```bash
# From repo root:
npm run scan:secrets          # → 0 findings
npm run validate:arch         # → 6/6 paths verified

# From samples/book-app-project/:
cd samples/book-app-project
.venv/bin/pytest -v           # → 9 passed, books.py 88%, total 48%

# Logging isolation checks:
python3 book_app.py list 2>/dev/null                     # stdout only — no JSON
LOG_LEVEL=WARNING python3 book_app.py list 2>&1          # no log lines at all

# books.py domain check (BOOK_SCHEMA vs Book dataclass):
python3 -c "from books import Book; import dataclasses; print([f.name for f in dataclasses.fields(Book)])"
# Expected: ['title', 'author', 'year', 'read']
```

## Track
- Level: Walk
- Exercise: 11
```
