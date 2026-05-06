# Exercise 13 — Feature Flag Lifecycle: `BOOK_APP_STRICT_YEAR`

## Mini Prompt
Document flag lifecycle and validate ON/OFF (CI matrix or documented local).

---

## Flag

**Name**: `BOOK_APP_STRICT_YEAR`  
**Type**: Environment variable  
**Default**: OFF (unset) — any integer year accepted  
**Truthy values**: `1`, `true`, `True`, `TRUE`, `yes`, `Yes`, `YES`  
**Falsy values**: unset, `""`, `0`, `false`, `no`, `off`

**Behaviour**:
- OFF → `parse_year()` accepts any integer year (current behaviour, no breaking change)
- ON → `parse_year()` enforces `1 <= year <= current_year`; out-of-range raises `ValueError`
- Blank input (`""`) always returns `0` regardless of flag state (blank = "unknown year")

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Reviewed `utils.py::parse_year()` — cleanest injection point for a range-guard | Confirmed |
| 2 | Added `import os`, `import datetime`, `_strict_year_enabled()` helper to `utils.py` | Done |
| 3 | Updated `parse_year()` to call range-guard when flag is ON | Done |
| 4 | Created `tests/test_feature_flags.py` — 25 tests: `TestStrictYearOff` (5) + `TestStrictYearOn` (20 incl. parametrize) | Done |
| 5 | Ran FLAG OFF: 25 passed | ✅ |
| 6 | Ran FLAG ON: 25 passed | ✅ |
| 7 | Ran full suite: 34 passed, coverage 48% → 55% | ✅ |
| 8 | Added `flag-matrix` job to `.github/workflows/walk-evidence.yml` (advisory matrix, both legs continue-on-error) | Done |
| 9 | Created `ai-track-docs/flag-lifecycle.md` — full lifecycle doc | Done |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Flag lifecycle documented | ✅ Pass — `ai-track-docs/flag-lifecycle.md` covers creation, default, enable, disable, removal checklist |
| ON state validated | ✅ Pass — 25/25 tests including 7 parametrized truthy values |
| OFF state validated | ✅ Pass — 25/25 tests including 5 parametrized falsy values |
| Tests updated | ✅ Pass — `tests/test_feature_flags.py` added (25 new tests) |
| CI matrix added | ✅ Pass — `flag-matrix` job in `walk-evidence.yml` with `flag_state: [off, on]` |

---

## Evidence

```
FLAG OFF (BOOK_APP_STRICT_YEAR=""):  25 passed in 0.44s
FLAG ON  (BOOK_APP_STRICT_YEAR=1):   25 passed in 0.18s
Full suite:                          34 passed in 0.32s
Coverage: 48% → 55% (utils.py now at 41%; books.py 88%; logging_config.py 100%)
```

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/utils.py` | Added `import os`, `import datetime`, `_strict_year_enabled()`, range-guard in `parse_year()` |
| `samples/book-app-project/tests/test_feature_flags.py` | New — 25 tests (ON/OFF classes + parametrize) |
| `.github/workflows/walk-evidence.yml` | Added `flag-matrix` advisory job with strategy matrix |
| `ai-track-docs/flag-lifecycle.md` | New — full flag lifecycle document |
| `ai-track-docs/onboarding-walk.md` | Exercise log updated with ex-13 |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 13 Feature Flag Lifecycle — BOOK_APP_STRICT_YEAR ON/OFF Validation

## Summary
- Introduced `BOOK_APP_STRICT_YEAR` env-var feature flag in `utils.py::parse_year()`.
- OFF (default): any integer year accepted — zero breaking change to existing behaviour.
- ON: years must satisfy `1 <= year <= current_year`; out-of-range raises `ValueError`.
- Added 25 tests (`TestStrictYearOff` + `TestStrictYearOn`) covering all truthy/falsy values.
- Added `flag-matrix` advisory CI job running both states on every PR.
- Documented full flag lifecycle in `ai-track-docs/flag-lifecycle.md`.
- Coverage improved: **48% → 55%** (34 tests total, up from 9).
- Files/paths touched:
  - `samples/book-app-project/utils.py`
  - `samples/book-app-project/tests/test_feature_flags.py` (new)
  - `.github/workflows/walk-evidence.yml` (flag-matrix job added)
  - `ai-track-docs/flag-lifecycle.md` (new)
  - `ai-track-docs/onboarding-walk.md` (ex-13 added)

## Evidence
- FLAG OFF:  `BOOK_APP_STRICT_YEAR="" pytest tests/test_feature_flags.py` → **25 passed in 0.44s**
- FLAG ON:   `BOOK_APP_STRICT_YEAR=1 pytest tests/test_feature_flags.py` → **25 passed in 0.18s**
- Full suite: `.venv/bin/pytest` → **34 passed in 0.32s**
- Coverage: 55% total | books.py 88% | logging_config.py 100%

## Risk & Rollback
- Risk: low — default is OFF; existing tests unaffected (9 original tests still pass)
- Rollback flag: `unset BOOK_APP_STRICT_YEAR` (no code change needed for rollback)
- Rollback code: `git revert <this-sha>` — removes `_strict_year_enabled()` and guard from `parse_year()`

## Review Focus
1. `utils.py::_strict_year_enabled()` — verify truthy set (`"1"`, `"true"`, `"yes"`) matches documented values in `flag-lifecycle.md` and test parametrize list exactly
2. `parse_year()` — confirm blank-input check (`if not year_str: return 0`) comes BEFORE the range guard, so blank always returns 0 in both states
3. `test_feature_flags.py` — confirm every `TestStrictYearOn` test uses `monkeypatch.setenv` and every `TestStrictYearOff` test uses `monkeypatch.delenv` (no test relies on ambient env state)
4. `flag-lifecycle.md` removal checklist — verify it lists all files that need updating when the flag is retired

## Track
- Level: Walk
- Exercise: 13
```
