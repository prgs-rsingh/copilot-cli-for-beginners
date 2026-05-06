# Exercise 04 — Onboarding Docs: CONTRIBUTING Walk Section + Onboarding Prompt

## Mini Prompt
Create/update CONTRIBUTING and an onboarding prompt file describing the Walk workflow.

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Read `CONTRIBUTING.md`, `README.md`, `.copilot-track/walk/prompt-exercise.md`, and `ai-track-docs/` listing to identify gaps | Found: no Walk-specific branching, PR, or prompt guidance in CONTRIBUTING; no onboarding prompt existed |
| 2 | Appended "Walk Track Workflow" section to `CONTRIBUTING.md` covering branching strategy, prompt structure, PR expectations, and exercise record convention | Added ~45 lines to existing doc |
| 3 | Created `ai-track-docs/onboarding-walk.md` — one-page prompt file covering repo context, workflow rules, PR format, test commands, conventions, and exercise log | Created new file |
| 4 | Updated `README.md` Contributing section with links to `CONTRIBUTING.md` and `ai-track-docs/onboarding-walk.md` | Added two descriptive link sentences |
| 5 | Ran `.venv/bin/pytest` — 5/5 passed, 36% total, books.py 87% | All green |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| CONTRIBUTING updated with Walk workflow | ✅ Pass — branching, prompt structure, PR expectations, exercise record all documented |
| Walk workflow clearly described | ✅ Pass — onboarding-walk.md covers all workflow rules in one pasteable page |
| Documentation linked in PR | ✅ Pass — README Contributing section links to both files |

---

## Files Changed

| File | Change |
|---|---|
| `CONTRIBUTING.md` | Appended "Walk Track Workflow" section (branching, prompt structure, PR expectations, exercise record, link to onboarding file) |
| `ai-track-docs/onboarding-walk.md` | Created — one-page Copilot Chat onboarding prompt |
| `README.md` | Added links to `CONTRIBUTING.md` and `onboarding-walk.md` in Contributing section |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 04 Onboarding Docs — CONTRIBUTING Walk Section + Onboarding Prompt

## Summary
- Identified gaps in `CONTRIBUTING.md`: no Walk-specific branching, PR, or prompt-structure guidance.
- Appended "Walk Track Workflow" section to `CONTRIBUTING.md` covering:
  branching strategy, prompt structure, PR expectations, and exercise record convention.
- Created `ai-track-docs/onboarding-walk.md` — a one-page prompt for pasting into Copilot Chat
  to orient a new contributor instantly (repo context, workflow rules, PR format, test commands, exercise log).
- Linked both files from `README.md` Contributing section.
- Plan: inline — additive doc-only change; no Walk section existed, so added rather than rewriting.
- Files/paths touched:
  - `CONTRIBUTING.md` (Walk Track Workflow section added)
  - `ai-track-docs/onboarding-walk.md` (new)
  - `README.md` (Contributing section updated with links)

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest` (from `samples/book-app-project/`) → 5 passed in 0.21s
- Coverage: 36% total (books.py 87%) — unchanged, doc-only exercise

## Risk & Rollback
- Risk: low
- Rollback: revert this commit (doc-only, no code changed)

## Review Focus
- Read `ai-track-docs/onboarding-walk.md` — confirm it fits in one page and covers enough context
  for a new contributor to start an exercise without further explanation
- Check `CONTRIBUTING.md` Walk section — verify branching and PR conventions match the pr-template.md
- Confirm `README.md` Contributing section links resolve correctly

## Track
- Level: Walk
- Exercise: 04
```
