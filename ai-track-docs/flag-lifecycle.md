# Feature Flag Lifecycle: `BOOK_APP_STRICT_YEAR`

## Overview

`BOOK_APP_STRICT_YEAR` is an environment-variable feature flag that tightens year
validation in `parse_year()` (`samples/book-app-project/utils.py`).

| Attribute | Value |
|---|---|
| Flag name | `BOOK_APP_STRICT_YEAR` |
| Type | Environment variable (string, truthy/falsy) |
| Default | **OFF** (unset) — any integer year is accepted |
| Introduced | Walk exercise 13 |
| Removal condition | When strict-year validation becomes the permanent default |

---

## Flag States

### OFF (default — unset or falsy value)

`parse_year()` accepts any integer year without range checking. Current behaviour
is preserved and no existing tests are affected.

**Falsy values** (all treated as OFF): unset, `""`, `"0"`, `"false"`, `"no"`, `"off"`

```bash
# Default — flag is off
python3 book_app.py

# Explicitly off
BOOK_APP_STRICT_YEAR=false python3 book_app.py
```

Behaviour:
- `""` → `0` (blank year)
- `"1949"` → `1949`
- `"9999"` → `9999` (accepted)
- `"0"` → `0` (accepted)
- `"abc"` → `ValueError` (non-numeric, always)

### ON

`parse_year()` additionally enforces `1 <= year <= current_year`. Any value outside
that range raises `ValueError` with a message that names the flag.

**Truthy values**: `"1"`, `"true"`, `"True"`, `"TRUE"`, `"yes"`, `"Yes"`, `"YES"`

```bash
BOOK_APP_STRICT_YEAR=1 python3 book_app.py
```

Behaviour:
- `""` → `0` (blank bypasses range check — blank means "unknown year")
- `"1949"` → `1949`
- `"9999"` → `ValueError: Year 9999 is out of range. Must be between 1 and <current_year>`
- `"0"` → `ValueError` (numeric zero is out of range)
- `"-100"` → `ValueError`
- `"abc"` → `ValueError` (non-numeric, always)

---

## Lifecycle

### 1 — Creation

Flag was introduced in `utils.py` via a private helper `_strict_year_enabled()`:

```python
def _strict_year_enabled() -> bool:
    return os.environ.get("BOOK_APP_STRICT_YEAR", "").lower() in ("1", "true", "yes")
```

`parse_year()` calls `_strict_year_enabled()` only after the blank check, so blank
input always returns `0` regardless of flag state.

### 2 — Default state

**OFF**. Existing behaviour is unchanged. No user-facing change without opting in.

### 3 — How to enable

```bash
# One-off for current shell session:
export BOOK_APP_STRICT_YEAR=1

# Per-command (doesn't persist):
BOOK_APP_STRICT_YEAR=1 python3 book_app.py

# In .env / devcontainer / CI:
BOOK_APP_STRICT_YEAR=1
```

### 4 — How to disable

```bash
unset BOOK_APP_STRICT_YEAR
# or set to a falsy value:
export BOOK_APP_STRICT_YEAR=false
```

### 5 — When to remove

Remove this flag when strict-year validation is adopted as the permanent default.
Removal checklist:
- [ ] Delete `_strict_year_enabled()` from `utils.py`
- [ ] Remove the `if _strict_year_enabled()` block from `parse_year()` — inline the strict logic unconditionally
- [ ] Delete `TestStrictYearOff` class from `tests/test_feature_flags.py` (permissive tests become irrelevant)
- [ ] Update `TestStrictYearOn` tests to remove `monkeypatch.setenv(...)` calls
- [ ] Remove `matrix.env_value` and `flag_state: off` leg from `.github/workflows/walk-evidence.yml`
- [ ] Update this document to mark flag as removed

---

## Validation

### Local — both states

```bash
cd samples/book-app-project

# OFF — permissive
BOOK_APP_STRICT_YEAR="" .venv/bin/pytest tests/test_feature_flags.py -v

# ON — strict
BOOK_APP_STRICT_YEAR=1 .venv/bin/pytest tests/test_feature_flags.py -v
```

### CI matrix

`.github/workflows/walk-evidence.yml` — job `flag-matrix` runs both:

```yaml
strategy:
  matrix:
    flag_state: ["off", "on"]
    include:
      - flag_state: "off"
        env_value: ""
      - flag_state: "on"
        env_value: "1"
```

Both legs are advisory (`continue-on-error: true`) and post results to the
GitHub Actions job summary.

---

## Validation Output (local, 2026-05-06)

### FLAG OFF (`BOOK_APP_STRICT_YEAR=""`)

```
collected 25 items

TestStrictYearOff::test_blank_returns_zero           PASSED
TestStrictYearOff::test_valid_historic_year          PASSED
TestStrictYearOff::test_future_year_accepted         PASSED
TestStrictYearOff::test_zero_year_accepted           PASSED
TestStrictYearOff::test_non_numeric_raises           PASSED
TestStrictYearOn::test_blank_still_returns_zero      PASSED
TestStrictYearOn::test_valid_historic_year           PASSED
TestStrictYearOn::test_current_year_accepted         PASSED
TestStrictYearOn::test_future_year_rejected          PASSED
TestStrictYearOn::test_far_future_year_rejected      PASSED
TestStrictYearOn::test_zero_year_rejected            PASSED
TestStrictYearOn::test_negative_year_rejected        PASSED
TestStrictYearOn::test_non_numeric_raises            PASSED
TestStrictYearOn::test_flag_truthy_values[1]         PASSED
TestStrictYearOn::test_flag_truthy_values[true]      PASSED
TestStrictYearOn::test_flag_truthy_values[True]      PASSED
TestStrictYearOn::test_flag_truthy_values[TRUE]      PASSED
TestStrictYearOn::test_flag_truthy_values[yes]       PASSED
TestStrictYearOn::test_flag_truthy_values[Yes]       PASSED
TestStrictYearOn::test_flag_truthy_values[YES]       PASSED
TestStrictYearOn::test_flag_falsy_values[0]          PASSED
TestStrictYearOn::test_flag_falsy_values[false]      PASSED
TestStrictYearOn::test_flag_falsy_values[no]         PASSED
TestStrictYearOn::test_flag_falsy_values[]           PASSED
TestStrictYearOn::test_flag_falsy_values[off]        PASSED

25 passed in 0.44s
```

### FLAG ON (`BOOK_APP_STRICT_YEAR=1`)

```
25 passed in 0.18s   ← same 25 tests; monkeypatch isolates each
```

### Full suite (both flag-test classes + original 9 tests)

```
Name                Stmts   Miss  Cover   Missing
books.py               65      8    88%   31-35, 51, 83-84
logging_config.py      22      0   100%
utils.py               41     24    41%   6-11, 15, 45-55, 60-70
TOTAL                 175     79    55%

34 passed in 0.32s
```

Coverage improved: 48% → **55%** (9 tests → 34 tests; 16 new statements covered in utils.py)

---

## Linked Paths

| Resource | Path |
|---|---|
| Flag implementation | `samples/book-app-project/utils.py` — `_strict_year_enabled()`, `parse_year()` |
| Flag tests | `samples/book-app-project/tests/test_feature_flags.py` |
| CI matrix job | `.github/workflows/walk-evidence.yml` — job `flag-matrix` |
