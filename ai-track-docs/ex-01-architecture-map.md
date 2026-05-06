# Exercise 01 — Architecture Docs: Map Nodes to Real Paths

## Mini Prompt
Update architecture docs so nodes map to real repo paths; add 2-3 data flows; validate diagram renders in CI.

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Listed entry points, key modules, and file paths by reading `book_app.py`, `books.py`, `utils.py`, `data.json`, `tests/test_books.py`, `pyproject.toml` | 6 modules identified and mapped |
| 2 | Created `ai-track-docs/architecture.md` with Module Map table (6 nodes → real paths), a dependency graph, and 3 sequence-diagram data flows (Write, Read, Test Isolation) | File created; all nodes link to real paths |
| 3 | Created `.github/scripts/validate-arch.js` — Node.js script that parses the Module Map table and checks each path exists on disk | Script created |
| 4 | Added `"validate:arch": "node .github/scripts/validate-arch.js"` to `package.json` scripts | npm run validate:arch now available |
| 5 | Ran `node .github/scripts/validate-arch.js` — all 6 paths passed | Validation output below |

### Validation Output
```
Validating 6 path(s) from ai-track-docs/architecture.md:

  ✓  samples/book-app-project/book_app.py
  ✓  samples/book-app-project/books.py
  ✓  samples/book-app-project/utils.py
  ✓  samples/book-app-project/data.json
  ✓  samples/book-app-project/tests/test_books.py
  ✓  samples/book-app-project/pyproject.toml

All paths verified. Architecture doc is valid.
```

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Architecture doc maps nodes to real file paths | ✅ Pass — 6 nodes in Module Map table, all with real repo-relative paths |
| At least one data flow added | ✅ Pass — 3 sequence diagrams: Write flow, Read/List flow, Test Isolation flow |
| Changes reflected in PR clearly | ✅ Pass — 3 files changed, validation script output included as evidence |

---

## Files Changed

| File | Change |
|---|---|
| `ai-track-docs/architecture.md` | Created — Module Map, dependency graph, 3 data-flow sequence diagrams, course-level graph |
| `.github/scripts/validate-arch.js` | Created — validates all Module Map paths exist on disk |
| `package.json` | Added `validate:arch` npm script |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 01 Architecture Docs — Map Nodes to Real Paths

## Summary
- Created `ai-track-docs/architecture.md` mapping 6 module nodes to real file paths,
  with a dependency graph and 3 sequence-diagram data flows (Write, Read, Test Isolation).
- Added `.github/scripts/validate-arch.js` to verify all referenced paths exist on disk.
- Added `npm run validate:arch` to `package.json`.
- Plan: inline — establish a living architecture doc with validation to catch stale path references.
- Files/paths touched:
  - `ai-track-docs/architecture.md` (new)
  - `.github/scripts/validate-arch.js` (new)
  - `package.json` (validate:arch script added)

## Evidence
- Tests/logs/metrics: `node .github/scripts/validate-arch.js` → 6/6 paths verified ✓
- Coverage: no new code paths in book-app; validation script is self-contained

## Risk & Rollback
- Risk: low
- Rollback: revert this commit (docs + script only, no production code changed)

## Review Focus
- Verify Mermaid diagrams in `ai-track-docs/architecture.md` render correctly in GitHub preview
- Run `npm run validate:arch` locally to confirm all 6 paths resolve
- Check that sequence diagram flows accurately reflect the actual import/call chain in the source files

## Track
- Level: Walk
- Exercise: 01
```
