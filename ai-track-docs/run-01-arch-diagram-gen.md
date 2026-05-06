# Run-01: Architecture Diagram Generation — book-app-project

## Mini Prompt
Automate architecture diagram generation or updates; produce a change summary showing what shifted since the last version.

## Subsystem in Scope
`samples/book-app-project/` — Python modules only (`books.py`, `book_app.py`, `utils.py`, `logging_config.py`, `resilience.py`)

## Out of Scope
- `samples/book-app-buggy/`, `samples/buggy-code/` — intentional bugs, do not touch
- `.venv/`, `__pycache__/`, `htmlcov/` — generated/vendor artifacts
- All other folders in the repo

## Patch Plan

### Phase 1 — Script
Create `.github/scripts/gen-arch-diagram.js`:
- Walk all `*.py` files in `samples/book-app-project/` (top-level only)
- Parse `import X` and `from X import Y` lines with regex to build a dependency graph
- Render a Mermaid `flowchart LR` diagram of intra-project dependencies
- Produce a module map table (file → purpose → key exports)
- Write `ai-track-docs/architecture.md`
- Write `ai-track-docs/.arch-manifest.json` (per-file line count + import edges + diagram hash) for future diffing
- If manifest already exists on disk: compute and print a change summary (added files, removed files, changed edges)
- Add `"gen:arch": "node .github/scripts/gen-arch-diagram.js"` to `package.json`

Acceptance: script exits 0, `ai-track-docs/architecture.md` and `.arch-manifest.json` created.

Phase 1 rollback: `rm .github/scripts/gen-arch-diagram.js ai-track-docs/architecture.md ai-track-docs/.arch-manifest.json` + revert `package.json`

### Phase 2 — Validate
- Run `npm run gen:arch` a second time — script detects existing manifest and prints "No changes since last run"
- Mutate one py file (add a blank line), re-run — script reports a line-count change
- Run `pytest` — confirm all 48 tests still pass

Phase 2 rollback: no additional files changed; rollback is same as Phase 1.

---

## Before Snapshot

```
ai-track-docs/        — empty (no architecture doc, no manifest)
No npm gen:arch script existed.

pytest (48 passed):
  books.py:         88%   resilience.py: 100%
  logging_config:  100%   TOTAL:          61%
```

## Steps Run

| Phase | Step | Outcome |
|---|---|---|
| Plan | Committed `run-01-arch-diagram-gen.md` (this file) as patch plan | ✅ |
| 1 | Created `.github/scripts/gen-arch-diagram.js` | ✅ |
| 1 | Added `"gen:arch"` npm script to `package.json` | ✅ |
| 2a | First run (no manifest) — 5 modules found, `architecture.md` + `.arch-manifest.json` written | ✅ |
| 2b | Second run (manifest exists) — "No changes detected since last run." | ✅ |
| 2c | Mutated `books.py` (blank line), re-ran — "1 change(s) … CHANGED: books.py (lines +1)" | ✅ |
| 2c | Reverted mutation | ✅ |
| 2d | `pytest` → 48 passed, 61% coverage — unchanged | ✅ |

## After Snapshot

```
ai-track-docs/architecture.md    — generated (Module Map + Mermaid diagram)
ai-track-docs/.arch-manifest.json — generated (manifest for diffing)
Diagram hash: 9244e2a554f7

npm run gen:arch output:
  📐 Architecture diagram generator
     Target: samples/book-app-project
     Modules found: 5
  📋 Change summary: No changes detected since last run.
  ✅ Written: ai-track-docs/architecture.md
  ✅ Written: ai-track-docs/.arch-manifest.json

pytest: 48 passed in 0.38s (unchanged)
```

## Measurable Outcome

| Metric | Before | After |
|---|---|---|
| Architecture docs | 0 | 1 (`ai-track-docs/architecture.md`) |
| Repeatable refresh command | none | `npm run gen:arch` |
| Change detection | none | manifest-based hash diff per file |
| Tests | 48 passed, 61% | 48 passed, 61% (unchanged) |

## Delegation Checklist

- [x] Patch plan created (scope, files, expected outcome)
- [x] File scope defined (`samples/book-app-project/*.py` only)
- [x] Diffs reviewed before committing (script logic reviewed)
- [x] Tests generated or updated (no new tests needed — script is a generator, not domain code)
- [x] Tests run and passing (48 passed)
- [x] Documentation updated (`ai-track-docs/architecture.md` is the doc)
- [x] Evidence captured (before/after snapshots above)
- [x] Rollback plan documented (in patch plan and in `architecture.md` itself)
- [x] Context file saved to `ai-track-docs/run-01-arch-diagram-gen.md`

## Acceptance Results

| Checkpoint | Status | Verification |
|---|---|---|
| Architecture diagram or doc generated | ✅ Pass | `cat ai-track-docs/architecture.md` — Module Map + Mermaid diagram present |
| Repeatable refresh process exists | ✅ Pass | `npm run gen:arch` → exits 0 |
| Change summary included | ✅ Pass | Second run: "No changes detected"; mutation run: "1 change(s) … CHANGED: books.py (lines +1)" |
| Rollback guidance present | ✅ Pass | Documented in patch plan and in `architecture.md` Rollback section |

## PR Description

```markdown
## Title
GHCP -- Run: 01 Architecture Diagram Generator — book-app-project

## Summary
- No architecture docs existed on disk. Created `.github/scripts/gen-arch-diagram.js`,
  a Node.js script that scans `samples/book-app-project/*.py` and generates:
  - `ai-track-docs/architecture.md` — Module Map table + Mermaid dependency flowchart
  - `ai-track-docs/.arch-manifest.json` — per-file hash manifest for change diffing
- Each subsequent `npm run gen:arch` run compares against the manifest and prints a
  change summary (added files, removed files, changed edges/line counts).
- Patch plan: `ai-track-docs/run-01-arch-diagram-gen.md`
- Files/paths touched:
  - `.github/scripts/gen-arch-diagram.js` (new)
  - `ai-track-docs/architecture.md` (generated)
  - `ai-track-docs/.arch-manifest.json` (generated)
  - `package.json` (added `gen:arch` script)

## Evidence
- Before: `ai-track-docs/` was empty; no repeatable diagram process existed
- After: `npm run gen:arch` → 5 modules mapped, Mermaid diagram written, diagram hash `9244e2a554f7`
- Change detection validated: blank-line mutation to `books.py` → "1 change(s) … CHANGED: books.py (lines +1)"
- Tests: 48 passed in 0.38s (unchanged from before)
- Delegation checklist: completed ✅

## Risk & Rollback
- Risk: low — generator writes only to `ai-track-docs/`; no Python source files modified
- Rollback: `rm ai-track-docs/architecture.md ai-track-docs/.arch-manifest.json`
- Rollback script: `git revert <sha>` to remove `gen-arch-diagram.js` and `package.json` change

## Track
- Level: Run
- Exercise: 01
```
