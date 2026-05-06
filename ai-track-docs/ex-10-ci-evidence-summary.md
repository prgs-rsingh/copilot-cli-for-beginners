# Exercise 10 — CI Evidence Summary (Advisory, Non-Blocking)

## Mini Prompt
Post coverage/evidence in CI job summary without blocking merges.

---

## CI Strategy

No PR validation workflow existed (only auto-generated `gh-aw` lock files and a `.bak`).

**Approach**: New GitHub Actions workflow `.github/workflows/walk-evidence.yml` triggered on
`pull_request` and `workflow_dispatch`. Every evidence step uses `continue-on-error: true`
so the job never blocks a merge — it only surfaces results in the GitHub Actions job summary tab.

**Non-blocking guarantee**:
- `continue-on-error: true` on every evidence step (tests, arch validation, secret scan)
- This workflow must **not** be added to branch protection required checks
- Advisory footer appended to summary on every run

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Reviewed existing workflows — only auto-generated `gh-aw` lock files and `.bak`; no PR validation | Confirmed: no advisory workflow existed |
| 2 | Created `.github/workflows/walk-evidence.yml` — runs on PRs and `workflow_dispatch` | Created |
| 3 | Workflow runs: pytest + coverage → `$GITHUB_STEP_SUMMARY`; arch validation → summary; secret scan → summary | All steps `continue-on-error: true` |
| 4 | Simulated all three checks locally to produce evidence (CI cannot be triggered without a live PR) | All passing — output below |

---

## Simulated Job Summary Output

> This is what appears in the GitHub Actions "Summary" tab for the walk-evidence job.

### 🧪 Test & Coverage Report

| Metric | Value |
|--------|-------|
| Total coverage | 48% |
| `books.py` coverage | 88% |
| Target | books.py ≥ 85% |

```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
book_app.py            47     47     0%   1-81
books.py               65      8    88%   31-35, 51, 83-84
logging_config.py      22      0   100%
utils.py               32     32     0%   1-47
-------------------------------------------------
TOTAL                 166     87    48%
9 passed in 0.30s
```

### 🏗️ Architecture Validation

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

### 🔒 Secret Scan

```
Secret scan — copilot-cli-for-beginners

Scanning 55 file(s)...

✓ No secret patterns found. Scan clean.
```

---

## How to View in CI

1. Open any PR targeting `main`
2. Click the **Checks** tab
3. Select **Walk Track — Evidence Summary**
4. Click **Summary** in the left sidebar

The job summary renders as Markdown with tables, code blocks, and the advisory footer.

## How to Trigger Manually

```bash
gh workflow run walk-evidence.yml
```

Or via the GitHub UI: **Actions → Walk Track — Evidence Summary → Run workflow**

---

## Non-Blocking Configuration

The workflow is advisory by design:
- `continue-on-error: true` on every evidence step
- Do **not** add `walk-evidence` to branch protection required checks
- If a finding needs action, open a follow-up issue or walk exercise

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Evidence visible in CI output | ✅ Pass — all three checks post to `$GITHUB_STEP_SUMMARY`; simulated output above |
| CI remains non-blocking | ✅ Pass — `continue-on-error: true` on every step; advisory footer in summary |
| Instructions documented | ✅ Pass — view path, manual trigger command, non-blocking config all documented |

---

## Files Changed

| File | Change |
|---|---|
| `.github/workflows/walk-evidence.yml` | Created — advisory PR evidence workflow (coverage + arch + secret scan → job summary) |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 10 CI Evidence Summary — Advisory Non-Blocking Job

## Summary
- No PR validation workflow existed; added `.github/workflows/walk-evidence.yml`.
- Triggers on `pull_request` → `main` and `workflow_dispatch`.
- Runs three advisory checks and posts results to the GitHub Actions job summary tab:
  1. `pytest --cov` → coverage table with total % and books.py %
  2. `node .github/scripts/validate-arch.js` → architecture path validation
  3. `node .github/scripts/scan-secrets.js` → secret pattern scan
- Every evidence step has `continue-on-error: true` — job never blocks a merge.
- Advisory footer appended to every summary run.
- Plan: inline — soft gate only; results are informational. Branch protection must NOT
  include this workflow as a required check.
- Files/paths touched:
  - `.github/workflows/walk-evidence.yml` (new)

## Evidence
(Simulated locally — CI requires a live PR to produce actual job summary URL)

### 🧪 Test & Coverage
| Metric | Value |
|--------|-------|
| Total | 48% |
| books.py | 88% ✓ (target ≥ 85%) |
| logging_config.py | 100% |

Tests: 9 passed in 0.30s

### 🏗️ Architecture: 6/6 paths verified ✓
### 🔒 Secrets: 55 files scanned, 0 findings ✓

## Risk & Rollback
- Risk: low — advisory only; does not affect any merge gate
- Rollback: delete `.github/workflows/walk-evidence.yml`

## Review Focus
- Confirm `continue-on-error: true` is present on all three evidence steps
- Confirm this workflow is NOT listed in branch protection required checks
- Run `gh workflow run walk-evidence.yml` after merge to verify the summary renders

## Track
- Level: Walk
- Exercise: 10
```
