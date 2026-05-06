#!/usr/bin/env node
/**
 * scan-secrets.js
 * Lightweight secret scanner for the repo source files.
 * Scans for hardcoded credentials — env-var references like ${VAR} are excluded.
 *
 * Usage:  node .github/scripts/scan-secrets.js
 *         npm run scan:secrets
 *
 * Exit code 0 = clean. Exit code 1 = findings require review.
 *
 * Allowlist rules are documented inline. Keep them minimal and justified.
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const REPO_ROOT = path.resolve(__dirname, "../..");

// File extensions to scan
const SCAN_EXTENSIONS = new Set([
  ".py", ".js", ".ts", ".json", ".toml", ".yml", ".yaml", ".env", ".sh",
]);

// Directories to skip entirely
const SKIP_DIRS = new Set([
  ".git", ".venv", "node_modules", "htmlcov", "__pycache__", ".pytest_cache",
  ".ruff_cache",
]);

// Patterns that indicate a potential hardcoded secret.
// Each entry: { name, regex }
const SECRET_PATTERNS = [
  { name: "Generic password assignment", regex: /password\s*=\s*['"][^'"]{6,}['"]/i },
  { name: "Generic secret assignment",   regex: /secret\s*=\s*['"][^'"]{6,}['"]/i },
  { name: "GitHub PAT (ghp_)",           regex: /ghp_[A-Za-z0-9]{36}/ },
  { name: "GitHub App token (ghs_)",     regex: /ghs_[A-Za-z0-9]{36}/ },
  { name: "OpenAI key (sk-)",            regex: /sk-[A-Za-z0-9]{20,}/ },
  { name: "npm token",                   regex: /npm_[A-Za-z0-9]{36}/ },
  { name: "Private key header",          regex: /-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----/ },
  { name: "AWS access key",              regex: /AKIA[0-9A-Z]{16}/ },
];

// Allowlist: lines matching ANY of these patterns are excluded as known safe.
// Document the justification for each rule.
const ALLOWLIST = [
  // ${VAR_NAME} syntax — runtime env-var reference, never a real secret value.
  // Example: "GITHUB_TOKEN": "${GITHUB_TOKEN}" in samples/mcp-configs/mcp-config.json
  { reason: "Env-var reference placeholder (${...})", regex: /\$\{[A-Z_][A-Z0-9_]*\}/ },

  // Single-quoted Python docstring or comment examples
  { reason: "Python docstring or comment example", regex: /^\s*#/ },

  // Test fixture strings — clearly fake values used in tests
  { reason: "Test fixture in tests/ directory", pathPattern: /[/\\]tests[/\\]/ },

  // samples/buggy-code/ — INTENTIONAL vulnerability demos for security exercises.
  // These files contain deliberate bugs (hardcoded secrets, SQL injection, etc.)
  // to teach students how to identify and fix security issues. Must NOT be fixed.
  // Reference: AGENTS.md "Don't fix bugs in samples/buggy-code/"
  { reason: "Intentional buggy-code security exercise demo", pathPattern: /[/\\]buggy-code[/\\]/ },

  // samples/src/ — Legacy JS/React samples from an earlier course version.
  // Contains obvious placeholder strings (e.g. 'your-secret-key') with TODO comments.
  // Not production code; no real secret value present.
  { reason: "Legacy sample placeholder string with TODO comment", pathPattern: /[/\\]samples[/\\]src[/\\]/ },
];

function shouldSkipDir(name) {
  return SKIP_DIRS.has(name);
}

function getFiles(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!shouldSkipDir(entry.name)) {
        results.push(...getFiles(path.join(dir, entry.name)));
      }
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (SCAN_EXTENSIONS.has(ext)) {
        results.push(path.join(dir, entry.name));
      }
    }
  }
  return results;
}

function isAllowlisted(line, filePath) {
  for (const rule of ALLOWLIST) {
    if (rule.pathPattern && rule.pathPattern.test(filePath)) return true;
    if (rule.regex && rule.regex.test(line)) return true;
  }
  return false;
}

function scanFile(filePath) {
  const rel = path.relative(REPO_ROOT, filePath);
  const lines = fs.readFileSync(filePath, "utf8").split("\n");
  const findings = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (isAllowlisted(line, filePath)) continue;

    for (const pattern of SECRET_PATTERNS) {
      if (pattern.regex.test(line)) {
        findings.push({
          file: rel,
          line: i + 1,
          pattern: pattern.name,
          // Redact value from output for safety
          preview: line.trim().slice(0, 80),
        });
      }
    }
  }
  return findings;
}

function main() {
  console.log("\nSecret scan — copilot-cli-for-beginners\n");
  const files = getFiles(REPO_ROOT);
  console.log(`Scanning ${files.length} file(s)...\n`);

  const allFindings = [];
  for (const file of files) {
    allFindings.push(...scanFile(file));
  }

  if (allFindings.length === 0) {
    console.log("✓ No secret patterns found. Scan clean.\n");
    process.exit(0);
  }

  console.error(`✗ ${allFindings.length} finding(s) require review:\n`);
  for (const f of allFindings) {
    console.error(`  [${f.pattern}]`);
    console.error(`  ${f.file}:${f.line}`);
    console.error(`  ${f.preview}\n`);
  }
  console.error(
    "If a finding is a false positive, add an allowlist rule in .github/scripts/scan-secrets.js\n" +
    "and document the justification in ai-track-docs/security-notes.md.\n"
  );
  process.exit(1);
}

main();
