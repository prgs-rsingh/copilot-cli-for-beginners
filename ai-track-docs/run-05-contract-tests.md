# Run-05: Contract Tests — BookCollection Interface Boundaries

## Mini Prompt
Add or validate contract tests for 1-2 boundaries and document the
update process. Sweep TODOs and edges across the API folder with rationale.

## Target
`books.py` — `BookCollection` is the primary interface boundary between the CLI
(`book_app.py`) and the persistence layer (`data.json`). No dedicated "API folder"
exists; this is the most interface-heavy module (troubleshooting note applied).

---

## Sweep Findings (Before)

| # | Gap / Edge | Location | Severity | Rationale |
|---|---|---|---|---|
| 1 | `remove_book()` returns `bool` but no contract test verified disk state after removal | `books.py:remove_book` | **High** | A bug in `save_books()` could return `True` while leaving stale data on disk |
| 2 | `add_book()` return type (`Book`) never asserted in any contract test | `books.py:add_book` | Medium | A future REST adapter or caller depends on the return type; silent breakage if changed |
| 3 | `find_by_author()` return type (`list[Book]`) and empty-list branch not contractually guarded | `books.py:find_by_author` | Medium | `utils.py:show_books` iterates the result; wrong type fails silently |
| 4 | Case-insensitive matching implicit but not pinned by a contract test | both find methods | Medium | A refactor removing `.lower()` normalization would not be caught |
| 5 | `save_books()` on empty collection (after removing last book) not tested | `books.py:save_books` | Low | Empty file or null would cause `JSONDecodeError` on next load |

---

## Files Changed

| File | Change |
|---|---|
| `tests/test_contract.py` | Added 5 contract tests (tests 5–9) + sweep comment block with update process |

## Out of Scope
- `books.py` source — no code changes needed (all findings are test gaps, not bugs)
- `samples/book-app-buggy/`, `samples/buggy-code/` — intentional bugs, do not touch

---

## New Contract Tests

| Test | Finding | Boundary Tested |
|---|---|---|
| `test_remove_book_round_trip` | #1 High | `remove_book()` → disk → reload — all three must agree |
| `test_add_book_return_type` | #2 Medium | `add_book()` returns `Book` with correct field values |
| `test_find_by_author_contract` | #3 Medium | `find_by_author()` returns `list[Book]`; returns `[]` on no match |
| `test_case_insensitive_lookup_contract` | #4 Medium | Both find methods match UPPER/lower/Mixed case |
| `test_empty_collection_persistence` | #5 Low | Empty collection → writes `[]` → reloads cleanly |

---

## Update Process (for future boundary changes)

Documented inline in `test_contract.py` (sweep comment block above test 5):

1. Change the `Book` dataclass field or `BookCollection` method signature.
2. Update `BOOK_SCHEMA` at the top of `test_contract.py` to match the new shape.
3. Regenerate `tests/fixtures/golden_book.json` with the new shape.
4. Run `pytest tests/test_contract.py` — all 9 contract tests must pass.
5. Update the sweep comment block with any new findings.

---

## Steps Run

| Step | Outcome |
|---|---|
| Committed `run-05-contract-tests.md` as patch plan | ✅ |
| Swept `books.py` interface for gaps — 5 findings | ✅ |
| Added 5 contract tests + sweep/update-process comment to `test_contract.py` | ✅ |
| `pytest tests/test_contract.py -v` → 9 passed | ✅ |
| Full suite `pytest --cov` → 90 passed, 98%, 0 regressions | ✅ |

---

## Evidence

### Contract tests run
```
tests/test_contract.py::test_save_books_schema_shape            PASSED
tests/test_contract.py::test_save_books_field_values            PASSED
tests/test_contract.py::test_round_trip_serialization           PASSED
tests/test_contract.py::test_golden_book_schema                 PASSED
tests/test_contract.py::test_remove_book_round_trip             PASSED  ← new (Finding 1)
tests/test_contract.py::test_add_book_return_type               PASSED  ← new (Finding 2)
tests/test_contract.py::test_find_by_author_contract            PASSED  ← new (Finding 3)
tests/test_contract.py::test_case_insensitive_lookup_contract   PASSED  ← new (Finding 4)
tests/test_contract.py::test_empty_collection_persistence       PASSED  ← new (Finding 5)
9 passed in 0.32s
```

### Full suite
```
book_app.py        47      0   100%
books.py           66      5    92%   33-37
logging_config.py  22      0   100%
resilience.py      27      0   100%
utils.py           43      0   100%
TOTAL             205      5    98%
90 passed in 0.53s
```

---

## Delegation Checklist

- [x] Patch plan created (scope, findings, expected outcome)
- [x] Sweep documented (5 findings with severity and rationale)
- [x] Contract tests added (5 new, each with rationale docstring)
- [x] Update process documented (in test file + context file)
- [x] Tests run and passing (90/90)
- [x] Evidence captured (before/after, test output)
- [x] Context file saved to `ai-track-docs/run-05-contract-tests.md`

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| At least one contract test added or strengthened | ✅ 5 new contract tests added |
| Validation process documented | ✅ 5-step update process in test file + context file |
| Tests run successfully | ✅ 90 passed, 0 failures |
| Update guidance for future changes included | ✅ Sweep comment block in `test_contract.py` |
| Rationale for each change documented | ✅ Docstring + sweep table per finding |

---

## PR Description

```markdown
## Title
GHCP -- Run: 05 Contract Tests — BookCollection Interface Boundary Sweep

## Summary
Swept `books.py` (`BookCollection` public interface) for contract test gaps.
Found 5: one high-severity (remove round-trip), three medium (return types,
case-insensitive), one low (empty collection persistence).
Added 5 new contract tests (tests 5–9) to `tests/test_contract.py`, each
with a rationale docstring and a sweep comment block documenting the update process.
No source code changes were needed — all findings were test gaps, not bugs.
Patch plan: `ai-track-docs/run-05-contract-tests.md`

## Evidence
- Before: 4 contract tests, 5 interface boundaries unguarded
- After: 9 contract tests, all 5 gaps closed
- `pytest tests/test_contract.py` → **9 passed**
- Full suite → **90 passed, 98%** — zero regressions

## Risk & Rollback
- Risk: none — test-only change; no source code modified
- Rollback: `git revert <sha>` removes the 5 new tests

## Track
- Level: Run
- Exercise: 05
```
