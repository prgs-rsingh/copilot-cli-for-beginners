# Exercise 05 — Contract Tests: data.json Schema + Golden File

## Mini Prompt
Add a contract test (schema/golden) for a boundary and integrate into CI if feasible.

---

## Boundary Identified

**`data.json` persistence schema** — the JSON format that `BookCollection.save_books()` produces
and `BookCollection.load_books()` consumes. This is the clearest contract surface in the repo:
it is the boundary between the domain layer (`books.py`) and any external consumer (storage, migrations, tooling).

**Authoritative schema** (from `BOOK_SCHEMA` in `test_contract.py`):

| Field | Type | Notes |
|---|---|---|
| `title` | `str` | non-empty |
| `author` | `str` | non-empty |
| `year` | `int` | positive |
| `read` | `bool` | defaults to `false` |

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Read `books.py` and `test_books.py` in full; confirmed no existing contract/schema tests | No contract tests found |
| 2 | Created `tests/fixtures/golden_book.json` — canonical one-record fixture representing a valid Book | Created |
| 3 | Created `tests/test_contract.py` with 4 contract tests (no new dependencies — stdlib `json` only) | Created |
| 4 | Ran `pytest tests/test_contract.py -v` — 4/4 passed | Verified |
| 5 | Ran `pytest -v` (full suite) — 9/9 passed; `books.py` 87% | All green |
| 6 | CI integration: `pyproject.toml` already has `testpaths = ["tests"]` — `test_contract.py` is auto-discovered; no CI config change needed | Confirmed |

---

## Contract Tests Added

| Test | What it checks |
|---|---|
| `test_save_books_schema_shape` | `save_books()` output is a JSON array; every record has exactly the 4 schema keys with correct types |
| `test_save_books_field_values` | Exact field values (including `read: true`) are preserved after `add_book` + `mark_as_read` |
| `test_round_trip_serialization` | A `Book` written by `save_books()` and loaded by a fresh `BookCollection` is bit-for-bit identical |
| `test_golden_book_schema` | Golden fixture `tests/fixtures/golden_book.json` conforms to `BOOK_SCHEMA` — guards against accidental field renames |

---

## How to update the contract when the schema changes intentionally

1. Update the `Book` dataclass in `books.py` (add/rename/remove the field).
2. Update `BOOK_SCHEMA` in `tests/test_contract.py` to reflect the new field and type.
3. Regenerate `tests/fixtures/golden_book.json` to include the new field:
   ```bash
   cd samples/book-app-project
   # Edit tests/fixtures/golden_book.json manually to match the new schema
   ```
4. Run `pytest tests/test_contract.py -v` — all 4 tests must pass before opening a PR.
5. Note the schema change in your PR description under **Summary** so reviewers know the contract shifted.

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| At least one contract test added | ✅ Pass — 4 contract tests across 2 new files |
| Contract test runs successfully | ✅ Pass — 4/4 contract tests passed; 9/9 full suite |
| Update instructions documented | ✅ Pass — 5-step update process above (also referenced in PR template) |

---

## CI Integration

No CI config changes needed. `pyproject.toml` already specifies:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```
`test_contract.py` sits in `tests/` and is auto-discovered by any `pytest` invocation, including CI.

---

## Test Output

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

TOTAL    134    86    36%
9 passed in 0.23s
```

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/tests/test_contract.py` | Created — 4 contract tests for `data.json` schema boundary |
| `samples/book-app-project/tests/fixtures/golden_book.json` | Created — golden fixture (1 canonical Book record) |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 05 Contract Tests — data.json Schema + Golden File

## Summary
- Identified `data.json` (the persistence boundary of `BookCollection`) as the contract surface.
- Added `tests/test_contract.py` with 4 contract tests using stdlib `json` (no new deps):
  - Schema shape: all 4 required fields present with correct types
  - Field values: exact values preserved after write + mark-as-read
  - Round-trip: save then fresh-load produces identical Book objects
  - Golden file: `tests/fixtures/golden_book.json` conforms to schema (guards field renames)
- CI integration: auto-discovered via existing `testpaths = ["tests"]` in `pyproject.toml` — no config change needed.
- Plan: inline — use stdlib only; golden file as a low-noise schema guard; update instructions in PR.
- Files/paths touched:
  - `samples/book-app-project/tests/test_contract.py` (new)
  - `samples/book-app-project/tests/fixtures/golden_book.json` (new)

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest -v` → 9 passed in 0.23s (5 existing + 4 new contract)
- Coverage: 36% total (books.py 87%) — unchanged

## Risk & Rollback
- Risk: low
- Rollback: revert this commit (test-only addition, no production code changed)

## Review Focus
- Verify `BOOK_SCHEMA` in `test_contract.py` matches the `Book` dataclass fields in `books.py` exactly
- Check `tests/fixtures/golden_book.json` has valid JSON and all 4 fields
- Run `.venv/bin/pytest tests/test_contract.py -v` to confirm 4/4 pass locally

## How to update the contract (for reviewers)
If `Book` dataclass fields change intentionally:
1. Update `BOOK_SCHEMA` in `test_contract.py`
2. Update `tests/fixtures/golden_book.json` to match
3. Run `pytest tests/test_contract.py -v` — all 4 must pass
4. Note the schema change in the PR Summary

## Track
- Level: Walk
- Exercise: 05
```
