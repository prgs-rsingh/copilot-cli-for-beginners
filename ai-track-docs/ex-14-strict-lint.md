# Exercise 14 — Strict Lint Gate on `books.py`

## Mini Prompt
Increase strictness on one path and gate it; document suppressions.

---

## Scope

**Target path**: `samples/book-app-project/books.py` (core domain module)  
**Tool**: `ruff` — rules `E` (style), `F` (pyflakes), `UP` (pyupgrade), `ANN` (annotations), `I` (isort)  
**Line length**: 120 (project standard)  
**Other files**: not in scope for the strict gate

---

## Findings Triage

| Finding | Code | Disposition | Rationale |
|---|---|---|---|
| Import block unsorted | I001 | **Fixed** | `asdict, dataclass` alphabetically; `logging_config` after stdlib |
| `typing.List` deprecated | UP035 / UP006 | **Fixed** | Replaced with built-in `list[Book]` |
| `typing.Optional` deprecated | UP045 | **Fixed** | Replaced with `Book \| None` |
| Unnecessary `"r"` mode | UP015 | **Fixed** | `open(DATA_FILE)` — read is default |
| Missing `-> None` on `__init__` | ANN204 | **Fixed** | Added explicit return type |
| Missing `-> None` on `load_books`, `save_books` | ANN201 | **Fixed** | Added explicit return types |
| Long `logger.info` lines | E501 | **Fixed** | Reformatted all logger calls to multiline dict style |
| Missing module docstring | D100 | **Not in scope** | D rules excluded from strict ruleset; module docstring added anyway |
| Missing class docstrings | D101 | **Suppressed** `# noqa: D101` | Educational dataclass — field names are self-documenting; not a library API |
| Missing `__init__` docstring | D107 | **Suppressed** `# noqa: D107` | `__init__` intent is trivial; docstring would be noise |
| Missing method docstrings | D102 | **Suppressed** `# noqa: D102` | Short one-liner methods; docstring would duplicate the method signature |
| `print()` found | T201 | **Suppressed** `# noqa: T201` | Intentional user-facing warning for corrupt data file; must reach stdout |
| `open()` not `Path.open()` | PTH123 | **Suppressed** `# noqa: PTH123` | Pathlib migration is a larger refactor tracked as backlog item 2 (`backlog.md`) |

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | `ruff check books.py --select ALL` → 26 findings | Triaged into fix / suppress categories |
| 2 | Fixed: I001, UP035, UP006, UP045, UP015, ANN201, ANN204, E501 | All fixed in one pass |
| 3 | Suppressed with inline `# noqa`: D101, D107, D102, T201, PTH123 | Comments include rationale |
| 4 | `ruff check books.py --select E,F,UP,ANN,I --line-length 120` → `All checks passed!` | ✅ |
| 5 | Added ruff config to `pyproject.toml`: `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]` | Done |
| 6 | Added `strict-lint` advisory CI job to `walk-evidence.yml` (scoped to `books.py`, `continue-on-error: true`) | Done |
| 7 | Full test suite: 34 passed, coverage 55% | ✅ |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Strictness increased for a defined path | ✅ Pass — `books.py` enforces E,F,UP,ANN,I; other files not in scope |
| High-signal findings resolved | ✅ Pass — 8 categories fixed |
| Suppressions documented | ✅ Pass — 5 suppression categories with inline rationale + table above |

---

## Evidence

```
ruff check books.py --select E,F,UP,ANN,I --line-length 120
→ All checks passed!

pytest (34 tests)
→ 34 passed in 0.33s
   books.py: 88%  |  logging_config.py: 100%  |  TOTAL: 55%
```

---

## Suppression Reference

All suppressions in `books.py` use inline `# noqa: <code>` with a trailing comment explaining why.

| noqa code | Location | Why suppressed |
|---|---|---|
| `D101` | `class Book`, `class BookCollection` | Dataclass fields are self-documenting; not a library with external consumers |
| `D107` | `def __init__` | Intent is trivial (`self.books = []`, `load_books()`) — docstring adds noise |
| `D102` | `add_book`, `list_books`, `find_book_by_title`, `mark_as_read` | Short, self-evident methods; signatures describe intent fully |
| `T201` | `print(...)` in JSONDecodeError handler | Must reach stdout — this is the user-facing warning for a corrupt data file |
| `PTH123` | Both `open(DATA_FILE...)` calls | Pathlib migration is a larger refactor tracked in `ai-track-docs/backlog.md` item 2 |

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/books.py` | Fixed 8 finding categories; added 5 documented suppressions; added module docstring |
| `samples/book-app-project/pyproject.toml` | Added `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]` sections |
| `.github/workflows/walk-evidence.yml` | Added `strict-lint` advisory job (scoped to `books.py`, non-blocking) |
| `ai-track-docs/onboarding-walk.md` | Exercise log updated with ex-14 |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 14 Strict Lint Gate — ruff E,F,UP,ANN,I on books.py

## Summary
- Scoped strict ruff lint to `books.py` (core domain module).
- Rules enforced: E (style), F (pyflakes), UP (pyupgrade), ANN (annotations), I (isort).
- Fixed 8 finding categories: unsorted imports, deprecated `typing.List`/`Optional`,
  redundant `"r"` mode, missing `-> None` return types, long logger.info lines.
- 5 suppression categories added with inline `# noqa` + rationale comment:
  - D101/D102/D107: docstrings — educational code, not library API
  - T201: intentional user-facing `print` in corrupt-file handler
  - PTH123: pathlib migration is a separate backlog item
- Added ruff config to `pyproject.toml` (`[tool.ruff.lint.per-file-ignores]` scopes strictness).
- Added `strict-lint` advisory CI job scoped to `books.py` only (non-blocking).
- All 34 tests pass; coverage unchanged at 55%.

## Evidence
- `ruff check books.py --select E,F,UP,ANN,I --line-length 120` → **All checks passed!**
- `.venv/bin/pytest` → **34 passed in 0.33s** | books.py 88% | TOTAL 55%

## Risk & Rollback
- Risk: low — logic unchanged; only imports, type annotations, and line formatting changed
- Rollback: `git revert <this-sha>` (also reverts pyproject.toml ruff config)
- The `strict-lint` CI job is `continue-on-error: true` — it cannot block merges

## Review Focus
1. **Suppression rationale** — verify each `# noqa` comment explains *why* it's suppressed,
   not just *what* it suppresses; confirm PTH123 links to the backlog
2. **ANN fixes** — `__init__ -> None`, `load_books -> None`, `save_books -> None` added;
   verify no return type was accidentally omitted or set to the wrong type
3. **Type annotation modernization** — `List[Book]` → `list[Book]`, `Optional[Book]` → `Book | None`;
   verify these work correctly on Python 3.10+ (requires-python = ">=3.10" in pyproject.toml ✓)
4. **CI job scope** — `strict-lint` job runs `ruff check books.py` only; confirm it does NOT
   run on other files (no glob like `ruff check .`)
5. **per-file-ignores** — verify `books.py` is NOT listed under `per-file-ignores`, confirming
   it receives the strictest treatment by default

## Track
- Level: Walk
- Exercise: 14
```
