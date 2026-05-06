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