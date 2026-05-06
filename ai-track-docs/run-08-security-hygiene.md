# Run-08: Security Hygiene — Atomic Write, Input Guard, Strict Deserialization

## Mini Prompt
Apply 2-3 security hygiene improvements plus documentation updates.
Autofix or create automated PRs for alerts (or a scripted patch set).

---

## Scan Results
`npm run scan:secrets` → **clean** (0 findings) before and after.
Manual review identified 3 hygiene issues in `samples/book-app-project/`.

## Findings

| # | Finding | File | Risk | OWASP |
|---|---|---|---|---|
| 1 | `save_books()` opens with `"w"` (truncate-then-write) — SIGKILL between truncate and complete write leaves `data.json` empty | `books.py:save_books` | Data loss / corruption | A04 Insecure Design |
| 2 | `parse_year()` passes unbounded user string to `int()` — 10,000-digit input causes large-int memory allocation | `utils.py:parse_year` | Resource exhaustion at input boundary | A03 Injection (CWE-190) |
| 3 | `load_books()` uses `Book(**b)` — extra/missing JSON keys raise unhandled `TypeError`, no schema guard at deserialization boundary | `books.py:load_books` | Crash on malformed/tampered data | A08 Data Integrity |

---

## Fixes Applied

### Fix 1 — Atomic write (`books.py:save_books`)
Write to `DATA_FILE + ".tmp"` then `os.replace()` (atomic rename on POSIX).
The real `data.json` is only replaced after the new content is fully written.
Added `import os` to `books.py`.

### Fix 2 — Year input cap (`utils.py:parse_year`)
Raise `ValueError` if `len(year_str) > 10` before calling `int()`.
10 digits > any plausible year; 3-line change; zero behavior change for normal input.

### Fix 3 — Strict deserialization (`books.py:load_books`)
Added `_BOOK_REQUIRED_FIELDS` and `_BOOK_ALLOWED_FIELDS` module-level constants.
Per-record validation before `Book(**record)`: skip with warning on unexpected/missing fields.
Valid records still load correctly; malformed records are skipped, not silently passed.

---

## Files Changed

| File | Changes |
|---|---|
| `books.py` | `import os`; `_BOOK_REQUIRED_FIELDS`/`_BOOK_ALLOWED_FIELDS` constants; atomic write in `save_books()`; per-record validation loop in `load_books()` |
| `utils.py` | 3-line length guard in `parse_year()` |
| `tests/test_utils.py` | `TestParseYearSecurity` — 2 tests for Fix 2 |
| `tests/test_security.py` | New — 8 tests: `TestAtomicWrite` (3) + `TestStrictDeserialization` (5) |
| `SECURITY.md` | New "Code Security Hygiene" section with scripted patch approach + update guidance |

---

## Steps Run

| Step | Outcome |
|---|---|
| Committed `run-08-security-hygiene.md` as patch plan | ✅ |
| `npm run scan:secrets` (baseline) → clean | ✅ |
| Manual review: 3 findings identified | ✅ |
| Fix 1 + Fix 3 applied to `books.py` | ✅ |
| Fix 2 applied to `utils.py` | ✅ |
| `tests/test_security.py` created (8 tests) | ✅ |
| `TestParseYearSecurity` added to `test_utils.py` (2 tests) | ✅ |
| New tests: 30 passed | ✅ |
| Full suite: **100 passed, 98%**, 0 regressions | ✅ |
| `npm run scan:secrets` (after) → clean | ✅ |
| `SECURITY.md` updated | ✅ |

---

## Evidence

```
$ .venv/bin/pytest --cov=. --cov-report=term-missing -q
book_app.py        47      0   100%
books.py           85      5    94%   54-58   ← only JSONDecodeError branch uncovered
logging_config.py  22      0   100%
resilience.py      27      0   100%
utils.py           41      0   100%
TOTAL             222      5    98%
100 passed in 0.64s

$ node .github/scripts/scan-secrets.js
Scanning 63 file(s)...
✓ No secret patterns found. Scan clean.
```

---

## Rollback Plan (per fix)

| Fix | Rollback |
|---|---|
| Fix 1 (atomic write) | Restore `open(DATA_FILE, "w")` direct write; remove `tmp_path` lines and `os` import |
| Fix 2 (year cap) | Remove 3-line `len(year_str) > 10` block from `parse_year()` |
| Fix 3 (strict deser.) | Replace validation loop with `self.books = [Book(**b) for b in data]`; remove two `_BOOK_*` constants |
| All | `git revert <sha>` |

---

## Scripted Re-audit Commands

Documented in `SECURITY.md`:
```bash
grep -n 'open.*"w"' samples/book-app-project/books.py
grep -n 'int(year' samples/book-app-project/utils.py
grep -n 'Book(\*\*' samples/book-app-project/books.py
.venv/bin/pytest tests/test_security.py -v
npm run scan:secrets
```

---

## Delegation Checklist

- [x] Patch plan created (findings, OWASP mapping, scope)
- [x] Security scan run (npm run scan:secrets — before and after)
- [x] 3 findings identified with risk and OWASP category
- [x] Fixes implemented (3 fixes, 2 source files)
- [x] Tests added (10 new: 2 in test_utils.py + 8 in test_security.py)
- [x] Full suite passing (100/100, 98%)
- [x] Security documentation updated (SECURITY.md — 3 fix docs + scripted approach + update guidance)
- [x] Rollback per fix documented
- [x] Context file saved to `ai-track-docs/run-08-security-hygiene.md`

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| At least one meaningful security improvement applied | ✅ 3 improvements: atomic write, input cap, strict deserialization |
| Security documentation updated | ✅ SECURITY.md new "Code Security Hygiene" section |
| Changes reviewed for side effects | ✅ 100 tests pass; scan clean |
| Evidence/justification included | ✅ OWASP mapping + rationale docstrings in each test |
| Scripted/repeatable patch approach documented | ✅ Re-audit commands in SECURITY.md + context file |

---

## PR Description

```markdown
## Title
GHCP -- Run: 08 Security Hygiene — Atomic Write, Input Guard, Strict Deserialization

## Summary
Manual review of `samples/book-app-project/` found 3 hygiene issues.
`npm run scan:secrets` was clean before and after.

**Fix 1 (A04):** `save_books()` non-atomic write → now writes to `.tmp` then `os.replace()`.
Prevents data.json corruption on process interrupt.

**Fix 2 (A03/CWE-190):** `parse_year()` unbounded `int()` → now rejects strings > 10 chars.
Prevents large-integer memory allocation at the user input boundary.

**Fix 3 (A08):** `Book(**b)` unguarded deserialization → now validates each JSON record
against `_BOOK_REQUIRED_FIELDS`/`_BOOK_ALLOWED_FIELDS` before construction.
Malformed records are skipped with a warning; valid records load as before.

10 new tests in `tests/test_security.py` + `tests/test_utils.py`.
`SECURITY.md` updated with fix docs, scripted re-audit commands, and update guidance.
Patch plan: `ai-track-docs/run-08-security-hygiene.md`

## Evidence
- `npm run scan:secrets` → clean (before and after)
- `pytest --cov` → **100 passed, 98%** — zero regressions
- OWASP categories documented per finding

## Risk & Rollback
- Risk: very low — behavior identical for valid inputs; all 90 pre-existing tests pass
- Rollback per fix: documented with exact code changes in SECURITY.md + context file
- Full rollback: `git revert <sha>`

## Track
- Level: Run
- Exercise: 08
```
