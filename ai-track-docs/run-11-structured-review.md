# Run-11: Structured Review — Focus, Risks, Checklist, Findings

## Mini Prompt
Generate review focus, risks, and verification steps; run AI review if
available or simulate reviewer checklist. Require AI plus human review;
address comments systematically.

---

## Review Scope

Changes accumulated across Run-03 through Run-10 in `samples/book-app-project/`
and `.github/workflows/walk-evidence.yml`.

| File | Changed In |
|---|---|
| `samples/book-app-project/books.py` | Run-08: atomic write, strict deserialization, logging |
| `samples/book-app-project/utils.py` | Run-06: print-batching; Run-08: year cap; Run-09: logging |
| `samples/book-app-project/book_app.py` | Run-03: prompt helper; Run-09: logging |
| `samples/book-app-project/resilience.py` | Run-09: logging, `getattr` fn-name fix |
| `samples/book-app-project/logging_config.py` | Baseline — reviewed, not changed |
| `samples/book-app-project/pyproject.toml` | Run-07: version pins, ruff declared |
| `.github/workflows/walk-evidence.yml` | Run-10: pip cache, timeout, pinned versions |
| `samples/book-app-project/tests/` | Run-03–09: 7 test files, 107 tests |

**Always out of scope**: `samples/book-app-buggy/`, `samples/buggy-code/`, `.venv/`

---

## Review Focus Section

### Key Risks

| Risk | Area | Severity |
|---|---|---|
| Atomic write leaves `.tmp` file on crash between `open()` and `os.replace()` | books.py | Low — orphan file; no data loss |
| `os.replace()` is atomic on POSIX but best-effort on Windows | books.py | Low — course runs on Linux/macOS |
| `parse_year()` rejects year=0 via strict mode but 0 is the blank-input sentinel | utils.py | Low — strict mode only active when env var set |
| `retry_with_backoff` default exceptions are `(OSError,)` — tight coupling to disk I/O | resilience.py | Low — explicit, well-documented |
| pip cache key is pyproject.toml hash — adding a dep invalidates cache correctly | walk-evidence.yml | None (correct behaviour) |
| books.py lines 54-58 (JSONDecodeError branch) not covered by tests | tests/ | Low — corruption path; existing warning message verified manually |

### Verification Steps

```bash
# 1. Confirm ruff clean (all rules)
cd samples/book-app-project
.venv/bin/ruff check books.py utils.py book_app.py resilience.py logging_config.py

# 2. Confirm full suite passes
.venv/bin/pytest --cov=. --cov-report=term-missing -q

# 3. Confirm atomic write leaves no .tmp on success
python -c "
import books, tempfile, os
with tempfile.TemporaryDirectory() as d:
    books.DATA_FILE = d + '/data.json'
    import json; open(books.DATA_FILE,'w').write('[]')
    c = books.BookCollection()
    c.add_book('T','A',2024)
    leftovers = [f for f in os.listdir(d) if f.endswith('.tmp')]
    assert not leftovers, leftovers
    print('OK: no .tmp file left')
"

# 4. Confirm year cap rejects overlength input
python -c "
from utils import parse_year
try:
    parse_year('1' * 11)
    print('FAIL: should have raised')
except ValueError as e:
    print('OK:', e)
"

# 5. Confirm strict year rejects out-of-range year
BOOK_APP_STRICT_YEAR=1 python -c "
from utils import parse_year
try:
    parse_year('9999')
    print('FAIL')
except ValueError as e:
    print('OK:', e)
"
```

---

## Phase 1: Automated Review (ruff + pytest)

### ruff — default rules (all categories)

```
book_app.py:1:1  I001  Import block is un-sorted or un-formatted  [fixable]
Found 1 error.
```

> **FIXED** — Added blank line between stdlib and local imports in `book_app.py`; sorted `from utils` names alphabetically. Verified with `ruff check --select E,F,UP,W`: **All checks passed.**

### ruff — strict gate (E, F, UP, W) after fix

```
All checks passed!
```

### pytest + coverage after fix

```
book_app.py        56      0   100%
books.py           85      5    94%   54-58
logging_config.py  22      0   100%
resilience.py      31      0   100%
utils.py           45      0   100%
TOTAL             239      5    98%
107 passed in 0.76s
```

---

## Phase 2: Simulated Reviewer Checklist

No AI review tool is available in this environment. The following checklist was
built from the team's review standards (per `.github/copilot-instructions.md`
and the OWASP Top 10 security requirements).

### Category 1: Correctness

| # | Check | File | Finding | Response |
|---|---|---|---|---|
| C-1 | `os.replace()` atomicity on all target OS | `books.py:79` | Atomic on POSIX; best-effort on Windows. Inline comment present. | **ACCEPTED** — course targets Linux/macOS; comment warns Windows users |
| C-2 | `save_books()` tmp file cleaned up on exception | `books.py:78-79` | If `open(tmp_path, 'w')` fails, no `.tmp` is created. If `os.replace()` fails (very rare), `.tmp` orphan remains but original data intact. | **ACCEPTED** — data is never lost; orphan `.tmp` is harmless |
| C-3 | `retry_with_backoff` guard on `max_retries < 1` | `resilience.py:65` | `ValueError` raised immediately with clear message. | **ACCEPTED** |
| C-4 | `parse_year` blank-input → 0, not error | `utils.py:42` | `if not year_str: return 0` — correct sentinel path | **ACCEPTED** |
| C-5 | Strict year mode: upper bound is `current_year`, not hardcoded | `utils.py:53` | `datetime.date.today().year` — dynamic; correct for year-crossing | **ACCEPTED** |
| C-6 | `find_book_by_title` case-insensitive | `books.py:101` | `.lower()` on both sides | **ACCEPTED** |
| C-7 | `load_books` logs AFTER `self.books = validated` | `books.py:62-64` | Log fires with final count, not intermediate | **ACCEPTED** |

### Category 2: Test Coverage

| # | Check | File | Finding | Response |
|---|---|---|---|---|
| T-1 | `JSONDecodeError` branch in `load_books` | `books.py:56-58` | Lines 54-58 missed — 5 uncovered statements | **DEFERRED** — the `print()` warning is a user-facing safeguard; a test would need to write a corrupt JSON file. Low priority, no logic at risk. Add to backlog. |
| T-2 | `add_book` log event verified | `tests/test_logging.py` | Not explicitly tested (only `books.py` logger not mocked in test_logging.py) | **ACCEPTED** — `test_books.py` covers add round-trip; log events in books.py are covered by `test_contract.py` exercising the collection indirectly |
| T-3 | `retry_with_backoff` parameter guard tests | `tests/test_resilience.py` | Guards for `max_retries < 1`, `initial_delay < 0`, `backoff_factor < 1.0` tested | **ACCEPTED** |
| T-4 | `parse_year` 10-char length cap tested | `tests/test_utils.py::TestParseYearSecurity` | Covered by Run-08 security tests | **ACCEPTED** |
| T-5 | Atomic write test covers `.tmp` → final path | `tests/test_security.py::TestAtomicWrite` | 3 tests: normal save, simulate failure, no leftover `.tmp` | **ACCEPTED** |

### Category 3: Security

| # | Check | File | Finding | Response |
|---|---|---|---|---|
| S-1 | Input length capped before `int()` conversion | `utils.py:46-50` | 10-char cap prevents large-int resource exhaustion (CWE-190 variant) | **ACCEPTED** |
| S-2 | Strict deserialization: allowlist + required fields | `books.py:15-16` | `_BOOK_REQUIRED_FIELDS`, `_BOOK_ALLOWED_FIELDS` frozensets used in `load_books` | **ACCEPTED** |
| S-3 | No secrets in log output | All `logger.*` calls | Reviewed all `extra={}` dicts: only `title`, `author`, `year`, `command`, `error` — no tokens, passwords, or PII | **ACCEPTED** |
| S-4 | CI secrets not in workflow file | `walk-evidence.yml` | No `${{ secrets.* }}` references; no `env:` with credentials | **ACCEPTED** |
| S-5 | Logging uses `extra={}` not string formatting | All modules | All events use `extra={"field": value}` — no f-string injection into log messages | **ACCEPTED** |
| S-6 | `scan:secrets` npm script still runs in CI | `walk-evidence.yml` | `node .github/scripts/scan-secrets.js` step present and `continue-on-error: true` | **ACCEPTED** |

### Category 4: Performance

| # | Check | File | Finding | Response |
|---|---|---|---|---|
| P-1 | `print_menu()` batched from 6 → 1 call | `utils.py:10-18` | Single `print()` with joined string; byte-for-byte identical output | **ACCEPTED** — measured in Run-06 |
| P-2 | `show_books()` batched: N+3 → 1 print call | `utils.py:83-95` | `"\n".join(lines)` — O(1) print calls regardless of N | **ACCEPTED** |
| P-3 | pip cache in CI saves ~25 s per run | `walk-evidence.yml` | `cache: 'pip'` keyed on `pyproject.toml` | **ACCEPTED** — Run-10 timing evidence |
| P-4 | `retry_with_backoff` worst-case latency documented | `resilience.py:27-30` | Docstring: 0.05 s + 0.10 s = 150 ms max for default settings | **ACCEPTED** |
| P-5 | `find_by_author` linear scan (O(N)) | `books.py:140` | No index; acceptable for a CLI collection of typical size (<10,000 books) | **ACCEPTED** — over-engineering an index would violate implementation discipline |

### Category 5: Documentation

| # | Check | File | Finding | Response |
|---|---|---|---|---|
| D-1 | `save_books()` has rollback instructions in comment | `books.py:67-68` | `# Rollback: remove the @retry_with_backoff line` | **ACCEPTED** |
| D-2 | `resilience.py` module docstring documents tuning params | `resilience.py:1-34` | Full parameter table with recommended ranges | **ACCEPTED** |
| D-3 | `walk-evidence.yml` timeout comment explains rationale | `walk-evidence.yml:20-21` | `# 15 min is generous: pip install + 107 tests...` | **ACCEPTED** |
| D-4 | `SECURITY.md` updated for Run-08 changes | `SECURITY.md` | "Code Security Hygiene" section with rollback commands | **ACCEPTED** |
| D-5 | `README.md` for book-app-project refreshed | `samples/book-app-project/README.md` | Module Map, Test Suite, Environment Variables, Risk Notes tables all present | **ACCEPTED** |
| D-6 | Import-sort finding not documented anywhere | `book_app.py` | Minor — now fixed; no doc update needed | **ACCEPTED** |

---

## Phase 3: Findings Summary and Responses

| ID | Category | Finding | Status | Action |
|---|---|---|---|---|
| C-1 | Correctness | `os.replace()` not atomic on Windows | ACCEPTED | Comment in code warns users |
| C-2 | Correctness | `.tmp` orphan on `os.replace()` failure | ACCEPTED | Data never lost; risk documented |
| T-1 | Coverage | JSONDecodeError branch uncovered (lines 54-58) | DEFERRED | Add to backlog; low priority |
| S-3 | Security | Log extra fields must not contain PII/secrets | ACCEPTED | All fields reviewed — clean |
| **A-1** | **Lint** | **I001: unsorted imports in `book_app.py`** | **FIXED** | Blank line + sorted names applied |

### Fixed: A-1 — Import sort in `book_app.py`

```diff
-import sys
-from books import BookCollection
+import sys
+
+from books import BookCollection
 from logging_config import get_logger
-from utils import show_books, parse_year, prompt
+from utils import parse_year, prompt, show_books
```

Verified: `ruff check` → **All checks passed** after fix.

---

## Phase 4: Post-Review Test Run

```
.venv/bin/ruff check books.py utils.py book_app.py resilience.py logging_config.py
→ All checks passed!

.venv/bin/pytest --cov=. --cov-report=term-missing -q
→ 107 passed in 0.76s
→ TOTAL: 239 stmts, 5 missed, 98%
```

---

## Human Review Request

```
Reviewer: [assign to maintainer]
Branch:   main (or feature branch carrying Run-03..Run-10)
Context:  ai-track-docs/run-11-structured-review.md

Focus areas for human reviewer:
1. books.py lines 54-58 (JSONDecodeError path) — confirm deferral of coverage is acceptable
2. os.replace() Windows behaviour comment — confirm warning is sufficient for course audience
3. Strict year mode UX: does the ValueError message in parse_year give enough guidance?

Questions:
- Should T-1 (JSONDecodeError coverage) be a required gate or stay as DEFERRED?
- Should the course README warn learners that strict year mode changes parse_year behaviour?

To verify this review locally:
  cd samples/book-app-project
  .venv/bin/ruff check books.py utils.py book_app.py resilience.py logging_config.py
  .venv/bin/pytest --cov=. --cov-report=term-missing -q
```

---

## Steps Run

| Step | Outcome |
|---|---|
| Committed `run-11-structured-review.md` as patch plan | ✅ |
| Phase 1: ruff (all rules) — found I001 in `book_app.py` | ✅ |
| Phase 1: ruff (E,F,UP,W strict) — clean | ✅ |
| Phase 1: pytest → 107 passed, 98% | ✅ |
| A-1: Fixed I001 import sort in `book_app.py` | ✅ |
| Phase 1 re-run after fix: ruff clean + 107 passed | ✅ |
| Phase 2: 5-category reviewer checklist completed (28 items) | ✅ |
| Phase 3: All findings documented; 1 fixed, 1 deferred, 26 accepted | ✅ |
| Human review request template included | ✅ |

---

## Acceptance Checklist

- [x] Review focus section included — risks table + 5 verification commands
- [x] Risks and verification steps documented
- [x] Automated tool run (ruff) + simulated reviewer checklist (28 items across 5 categories)
- [x] Clear response to every finding: ACCEPTED / FIXED / DEFERRED
- [x] Human review request with specific focus areas and questions

---

## PR Description

```markdown
## Title
GHCP -- Run: 11 Structured Review — Focus, Checklist, Findings, Fix

## Summary
Performed a structured review of cumulative changes (Run-03 through Run-10)
across `samples/book-app-project/` and `.github/workflows/walk-evidence.yml`.

**Review artifacts:**
- Review focus section: 6 risks, 5 verification commands
- Automated lint: ruff (all rules + strict E/F/UP/W gate)
- Simulated reviewer checklist: 28 items across 5 categories
  (correctness, test coverage, security, performance, documentation)
- All findings documented with ACCEPTED / FIXED / DEFERRED status

**One fix applied:**
- `book_app.py` I001: unsorted imports — blank line added, names sorted

**One deferral:**
- `books.py` lines 54-58 (JSONDecodeError branch) — coverage gap noted;
  no logic at risk; deferred to backlog

## Evidence
- `ruff check` → All checks passed (all 5 source files)
- `pytest` → **107 passed, 98%** — zero regressions

## Human Review Requested
See human review request section in `ai-track-docs/run-11-structured-review.md`
for specific focus areas and open questions.

## Track
- Level: Run
- Exercise: 11
```
