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

## Secret Hygiene

### What must never be committed

| Type | Examples | Correct alternative |
|------|----------|-------------------|
| API keys / tokens | `sk_live_…`, `ghp_…`, `AKIA…` | `process.env.MY_KEY` / `os.environ["MY_KEY"]` |
| JWT secrets | any hardcoded signing key | env var with startup guard |
| Private keys / certs | `*.pem`, `*.key`, `*.p12`, `*.pfx` | secrets manager or CI secret store |
| Cloud credentials | `.aws/credentials`, `gcp-credentials.json`, `serviceAccountKey.json` | IAM roles / workload identity |
| `.env` files with real values | `.env.production` | `.env.example` (values redacted) only |

### `.gitignore` coverage (enforced in this repo)

The repo `.gitignore` blocks:
- `.env` and `.env.*` (all variants) — except `.env.example`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.cert`, `*.crt`
- `*_credentials.json`, `serviceAccountKey.json`, `gcp-credentials.json`, `.aws/`
- `.venv/`, `venv/`, `env/` — Python virtual environments

### Intentional buggy samples

`samples/buggy-code/` and `samples/book-app-buggy/` contain **deliberate
security anti-patterns** (hardcoded secrets, SQL injection, etc.) for course
exercises.  These files are safe to keep as-is because they contain only
fake/test values.  Do not copy patterns from these files into production code.

### Pre-commit check

Before opening a PR, run a quick scan for accidental secrets:

```bash
# Requires truffleHog or git-secrets; basic grep alternative:
grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}" \
  samples/book-app-project/ samples/book-app-project-js/ samples/src/
```

Any match outside `samples/buggy-code/` or `samples/book-app-buggy/` should
be replaced with an environment variable before merging.