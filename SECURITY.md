Thanks for helping make GitHub safe for everyone.

# Security

GitHub takes the security of our software products and services seriously, including all of the open source code repositories managed through our GitHub organizations, such as [GitHub](https://github.com/GitHub).

Even though [open source repositories are outside of the scope of our bug bounty program](https://bounty.github.com/index.html#scope) and therefore not eligible for bounty rewards, we will ensure that your finding gets passed along to the appropriate maintainers for remediation. 

## Reporting Security Issues

If you believe you have found a security vulnerability in any GitHub-owned repository, please report it to us through coordinated disclosure.

**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Instead, please send an email to opensource-security[@]github.com.

Please include as much of the information listed below as you can to help us better understand and resolve the issue:

  * The type of issue (e.g., buffer overflow, SQL injection, or cross-site scripting)
  * Full paths of source file(s) related to the manifestation of the issue
  * The location of the affected source code (tag/branch/commit or direct URL)
  * Any special configuration required to reproduce the issue
  * Step-by-step instructions to reproduce the issue
  * Proof-of-concept or exploit code (if possible)
  * Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Policy

See [GitHub's Safe Harbor Policy](https://docs.github.com/en/site-policy/security-policies/github-bug-bounty-program-legal-safe-harbor#1-safe-harbor-terms)

---

## Secret Scanning

This repo includes a lightweight secret scanner to prevent accidental credential commits.

### Run locally

```bash
npm run scan:secrets
```

The scanner checks all source files (`.py`, `.js`, `.json`, `.toml`, `.yml`, `.yaml`, `.sh`) for common secret patterns: hardcoded passwords, API keys, GitHub tokens, private key headers, and AWS access key IDs.

Exit code `0` = clean. Exit code `1` = findings require review.

### CI integration

When `gitleaks` is available in CI, use the provided `.gitleaks.toml` config:

```bash
gitleaks detect --source . --config .gitleaks.toml --redact
```

### Adding a justified ignore

If the scanner flags a known-safe pattern (false positive), do **not** disable the scanner. Instead:

1. Add a rule to the `ALLOWLIST` array in `.github/scripts/scan-secrets.js`
2. Document the justification inline as a comment
3. Add a corresponding entry to `.gitleaks.toml` under `[allowlist]`
4. Open a PR — the justification must be reviewed before merging

### Known justified ignores

| File / Path | Pattern | Justification |
|---|---|---|
| `samples/mcp-configs/mcp-config.json` | `"GITHUB_TOKEN": "${GITHUB_TOKEN}"` | Env-var reference placeholder — reads from runtime environment, never a real value |
| `samples/buggy-code/` | Hardcoded `JWT_SECRET` | **Intentional** vulnerability demos for security exercises (per `AGENTS.md`, must not be fixed) |
| `samples/src/` | `'your-secret-key'` placeholder | Legacy sample with `TODO: Move to environment variable` comment — not a real secret |

### Important note on `samples/buggy-code/`

The files in `samples/buggy-code/` contain **deliberate security vulnerabilities** including hardcoded credentials. This is by design — they are teaching material for security exercises. Do not report these as vulnerabilities and do not fix them.

---

## Code Security Hygiene (book-app-project)

The following security hygiene fixes were applied to `samples/book-app-project/` in Run-08.
Each fix is tested in `tests/test_security.py` with rationale comments and rollback guidance.

### Fix 1 — Atomic write in `save_books()` (`books.py`)

**Risk:** `open(DATA_FILE, "w")` truncates the file immediately. A SIGKILL or power loss between
truncate and write completion leaves `data.json` empty — permanent data loss.

**Fix:** Write to `DATA_FILE + ".tmp"` then call `os.replace()` (atomic rename on POSIX, best-effort on Windows).
The real `data.json` is only replaced after the new content is fully written.

**Rollback:**
```bash
# In books.py save_books(), replace:
#   tmp_path = DATA_FILE + ".tmp"
#   with open(tmp_path, "w") as f: ...
#   os.replace(tmp_path, DATA_FILE)
# With:
#   with open(DATA_FILE, "w") as f: ...
```

**Test:** `tests/test_security.py::TestAtomicWrite`

---

### Fix 2 — Input length cap in `parse_year()` (`utils.py`)

**Risk:** `int(year_str)` with no length bound — a 10,000-digit string causes Python's
arbitrary-precision integer to allocate significant memory (CWE-190 variant).
At a system boundary (user input), this is a resource exhaustion vector.

**Fix:** Raise `ValueError` if `len(year_str) > 10` before calling `int()`.
10 digits is 3× longer than any plausible year (max: 9,999); provides a safety margin.

**Rollback:**
```bash
# In utils.py parse_year(), remove the three lines:
#   if len(year_str) > 10:
#       raise ValueError(...)
```

**Test:** `tests/test_utils.py::TestParseYearSecurity`

---

### Fix 3 — Strict field validation in `load_books()` (`books.py`)

**Risk:** `Book(**b)` on a JSON record with unexpected keys raises `TypeError` — an
unhandled exception that crashes the app. A corrupted or tampered `data.json` can exploit this.

**Fix:** Validate each record against `_BOOK_REQUIRED_FIELDS` and `_BOOK_ALLOWED_FIELDS`
before constructing `Book`. Malformed records are skipped with a warning; valid records load normally.

**Rollback:**
```bash
# In books.py load_books(), replace the per-record validation loop with:
#   self.books = [Book(**b) for b in data]
# Remove the _BOOK_REQUIRED_FIELDS and _BOOK_ALLOWED_FIELDS module-level constants.
```

**Test:** `tests/test_security.py::TestStrictDeserialization`

---

### Scripted patch approach

All three fixes are contained in two files (`books.py`, `utils.py`) and are independently rollback-able.
To re-audit the codebase for these patterns in the future:

```bash
# Check for non-atomic file writes (open with "w" not followed by os.replace)
grep -n 'open.*"w"' samples/book-app-project/books.py

# Check for unbounded int() on user input
grep -n 'int(year' samples/book-app-project/utils.py

# Check for unvalidated **kwargs deserialization from external data
grep -n 'Book(\*\*' samples/book-app-project/books.py

# Run full security test suite
cd samples/book-app-project && .venv/bin/pytest tests/test_security.py -v

# Run secret scanner
npm run scan:secrets
```

### Update guidance for future hygiene changes

1. Add the fix to the relevant source file.
2. Add or update tests in `tests/test_security.py` with a rationale docstring and rollback note.
3. Update this section of `SECURITY.md` with the fix description and rollback command.
4. Run `pytest --cov` — all tests must pass, coverage must not drop.
5. Run `npm run scan:secrets` — must remain clean.
6. Commit source + tests + docs in a single PR (code and doc in the same PR).