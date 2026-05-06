# Exercise 08 — Secret Scanning: Lightweight Scanner + Justified Ignores

## Mini Prompt
Add or improve a lightweight scanning step and remediate one issue or add justified ignore.

---

## Evaluation: Pre-existing Scanning

- No CI workflows active (only `.lock.yml` stubs in `.github/workflows/`)
- No `.pre-commit-config.yaml`
- No gitleaks, trufflehog, or detect-secrets installed locally
- No allowlist config files

**Action**: add a lightweight Node.js scanner script (zero new deps), a `.gitleaks.toml`
allowlist for CI, and `npm run scan:secrets` entry point.

---

## Scan Findings and Disposition

Initial scan (before allowlist rules) found **3 findings**:

| # | File | Line | Pattern | Disposition |
|---|---|---|---|---|
| 1 | `samples/buggy-code/js/userService.js:59` | `JWT_SECRET = 'super-secret-key-12345'` | Generic secret assignment | **Justified ignore** — intentional vulnerability demo for security exercises (`AGENTS.md`: must not be fixed) |
| 2 | `samples/buggy-code/python/user_service.py:71` | `JWT_SECRET = "super-secret-key-12345"` | Generic secret assignment | **Justified ignore** — same as above (Python equivalent) |
| 3 | `samples/src/api/auth.js:9` | `JWT_SECRET = 'your-secret-key'` | Generic secret assignment | **Justified ignore** — legacy sample placeholder with `TODO: Move to environment variable` comment; not a real secret |

All three are **educational courseware** — not production credentials. Allowlist rules added with inline justification comments.

**After allowlist rules**: `✓ No secret patterns found. Scan clean.` (52 files scanned)

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Checked for existing scanners (`gitleaks`, `trufflehog`, `detect-secrets`) — none found locally or in CI | Confirmed: no scanning existed |
| 2 | Grep-scanned all source files for secret patterns to understand the real baseline | Found 1 env-var ref (`mcp-config.json`) and 3 intentional buggy-code patterns |
| 3 | Created `.github/scripts/scan-secrets.js` — Node.js scanner with configurable patterns and allowlist | Created |
| 4 | Ran scanner: 3 findings from intentional buggy-code and legacy samples | Evidence captured |
| 5 | Added 2 path-based allowlist rules (`samples/buggy-code/`, `samples/src/`) with inline justifications | Allowlist updated |
| 6 | Re-ran scanner: clean (52 files, 0 findings) | ✓ Scan clean |
| 7 | Created `.gitleaks.toml` with matching allowlist for CI use when gitleaks is added | Created |
| 8 | Added `scan:secrets` to `package.json` scripts | Done |
| 9 | Updated `SECURITY.md` with scanning process, run instructions, CI guidance, add-ignore process, and known-justified-ignores table | Done |
| 10 | Ran `.venv/bin/pytest` — 9/9 passed | No regression |

---

## Scan Output (after allowlist)

```
Secret scan — copilot-cli-for-beginners

Scanning 52 file(s)...

✓ No secret patterns found. Scan clean.
```

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Scan step added | ✅ Pass — `npm run scan:secrets` via `.github/scripts/scan-secrets.js`; `.gitleaks.toml` for CI |
| At least one security improvement or justified ignore | ✅ Pass — 3 findings triaged and documented; allowlist rules added with inline justification |
| Security notes updated | ✅ Pass — `SECURITY.md` updated with scanning section, known ignores table, and add-ignore process |

---

## Files Changed

| File | Change |
|---|---|
| `.github/scripts/scan-secrets.js` | Created — Node.js secret scanner (8 patterns, 5 allowlist rules) |
| `.gitleaks.toml` | Created — gitleaks config for CI with documented allowlist |
| `package.json` | Added `scan:secrets` npm script |
| `SECURITY.md` | Added "Secret Scanning" section with process, CI guidance, and known ignores table |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 08 Secret Scanning — Lightweight Scanner + Documented Justified Ignores

## Summary
- No secret scanning existed in the repo (no CI workflows active, no pre-commit hooks, no tools installed).
- Added `.github/scripts/scan-secrets.js`: zero-dependency Node.js scanner checking 8 secret
  patterns across 52 source files; configurable allowlist with inline justification comments.
- Added `npm run scan:secrets` entry point.
- Added `.gitleaks.toml` allowlist config for future CI integration with gitleaks.
- Initial scan found 3 findings — all intentional courseware (buggy-code demos + legacy placeholder).
  Added 2 path-based allowlist rules with documented justifications.
- Re-scan: ✓ clean (52 files, 0 findings).
- Updated `SECURITY.md` with scanning process, run command, CI guidance, add-ignore process,
  and known-justified-ignores table.
- Plan: inline — lightweight, no new runtime deps; scanner runs in ~1s locally.
- Files/paths touched:
  - `.github/scripts/scan-secrets.js` (new)
  - `.gitleaks.toml` (new)
  - `package.json` (scan:secrets added)
  - `SECURITY.md` (Secret Scanning section added)

## Evidence
- Tests/logs/metrics:
  - `npm run scan:secrets` → Scanning 52 file(s)... ✓ No secret patterns found. Scan clean.
  - `.venv/bin/pytest` → 9 passed in 0.14s
- Coverage: 36% total (books.py 86%) — unchanged

## Risk & Rollback
- Risk: low — scan script is read-only; `.gitleaks.toml` only activates when gitleaks is installed
- Rollback: revert this commit (no production code changed)

## Review Focus
- Run `npm run scan:secrets` to confirm clean result
- Review allowlist rules in `scan-secrets.js` — confirm each path-based exclusion is justified
- Check `SECURITY.md` known-ignores table against AGENTS.md to confirm buggy-code policy alignment
- Verify `.gitleaks.toml` `[allowlist]` matches the `scan-secrets.js` allowlist rules

## Track
- Level: Walk
- Exercise: 08
```
