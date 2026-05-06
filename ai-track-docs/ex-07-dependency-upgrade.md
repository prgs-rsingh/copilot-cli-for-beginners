# Exercise 07 — Dependency Upgrade: pip 25.2 → 26.1.1

## Mini Prompt
Upgrade one minor dependency safely; document impact and rollback.

---

## Upgrade Candidate Selection

Running `pip list --outdated` revealed:

| Package | Installed | Latest | Type |
|---|---|---|---|
| `pip` | 25.2 | 26.1.1 | wheel |

**Finding**: all declared project dependencies (`pytest 9.0.3`, `pytest-cov 7.1.0`) and all
transitive dependencies (`coverage`, `pluggy`, `iniconfig`, `packaging`, `pygments`) are
already at their latest versions. The only available upgrade is `pip` itself.

`pip` is the package installer used to manage the venv — not an application runtime dependency.
Upgrading it carries minimal risk: it does not affect test execution, application logic, or
the `data.json` schema.

**Version delta**: 25.2 → 26.1.1 (pip uses calendar-ish versioning; this is the next
release cycle, equivalent to a minor upgrade in conventional semver terms).

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Ran `pip list --outdated` — only `pip` 25.2 → 26.1.1 available; all project deps at latest | Honest finding documented |
| 2 | Recorded baseline: `pip 25.2` | Baseline captured |
| 3 | Upgraded: `.venv/bin/pip install --upgrade "pip==26.1.1"` | Successfully installed pip 26.1.1 |
| 4 | Ran `.venv/bin/pytest -v` — 9/9 passed, coverage unchanged | Clean upgrade confirmed |
| 5 | Added pip version comment + rollback command to `pyproject.toml` | Documented |

---

## Before / After

| | Before | After |
|---|---|---|
| pip version | 25.2 | 26.1.1 |
| pytest | 9.0.3 | 9.0.3 (unchanged) |
| pytest-cov | 7.1.0 | 7.1.0 (unchanged) |
| Test results | 9/9 passed | 9/9 passed |
| books.py coverage | 86% | 86% (unchanged) |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Minor upgrade applied | ✅ Pass — pip 25.2 → 26.1.1 |
| Tests verified | ✅ Pass — 9/9 passed, 36% total, books.py 86% |
| Rollback instructions included | ✅ Pass — documented in pyproject.toml comment and below |

---

## Rollback

To revert pip to the previous version:

```bash
cd samples/book-app-project
.venv/bin/pip install "pip==25.2"
```

No application code changes are required — the upgrade touches only the package installer inside the venv.

---

## Test Output (after upgrade)

```
tests/test_books.py::test_add_book PASSED
tests/test_books.py::test_mark_book_as_read PASSED
tests/test_books.py::test_mark_book_as_read_invalid PASSED
tests/test_books.py::test_remove_book PASSED
tests/test_books.py::test_remove_book_invalid PASSED
tests/test_contract.py::test_save_books_schema_shape PASSED
tests/test_contract.py::test_save_books_field_values PASSED
tests/test_contract.py::test_round_trip_serialization PASSED
tests/test_contract.py::test_golden_book_schema PASSED

TOTAL    136    87    36%
9 passed in 0.24s
```

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/pyproject.toml` | Added pip version comment and rollback command |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 07 Dependency Upgrade — pip 25.2 → 26.1.1

## Summary
- Ran `pip list --outdated`: all declared project dependencies (`pytest 9.0.3`,
  `pytest-cov 7.1.0`) and all transitive deps are already at their latest versions.
- Only available upgrade: `pip` itself — 25.2 → 26.1.1 (next release cycle;
  equivalent to a minor upgrade).
- Applied upgrade: `.venv/bin/pip install --upgrade "pip==26.1.1"` — clean install,
  no code changes needed.
- Documented pip version and rollback command in `pyproject.toml` comment.
- Plan: inline — pip-only upgrade; no application logic or schema changes.
- Files/paths touched:
  - `samples/book-app-project/pyproject.toml` (pip version comment added)

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest -v` (after upgrade) → 9 passed in 0.24s
- Coverage: 36% total (books.py 86%) — unchanged

## Risk & Rollback
- Risk: low — pip is a dev-time tool; does not affect application logic, test execution, or data schema
- Rollback: `.venv/bin/pip install "pip==25.2"` (no code revert required)

## Review Focus
- Confirm `pip --version` in the venv reports 26.1.1 after pulling and activating `.venv`
- Run `.venv/bin/pytest -v` to confirm 9/9 green
- Note: if other contributors recreate the venv from scratch, they will get the pip version
  bundled with their Python install; the comment in `pyproject.toml` documents the intended version

## Track
- Level: Walk
- Exercise: 07
```
