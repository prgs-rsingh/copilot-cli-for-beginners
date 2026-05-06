#!/usr/bin/env node
/**
 * validate-arch.js
 * Reads ai-track-docs/architecture.md and verifies that every file path
 * referenced in the Module Map table actually exists on disk.
 *
 * Usage:  node .github/scripts/validate-arch.js
 *         npm run validate:arch
 */

const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "../..");
const ARCH_DOC = path.join(REPO_ROOT, "ai-track-docs", "architecture.md");

function extractPaths(content) {
  const paths = [];
  // Match table rows like: | ... | `samples/book-app-project/books.py` |
  const tableRowRe = /\|\s*[^|]+\|\s*`([^`]+)`\s*\|/g;
  let m;
  while ((m = tableRowRe.exec(content)) !== null) {
    paths.push(m[1].trim());
  }
  return paths;
}

function main() {
  if (!fs.existsSync(ARCH_DOC)) {
    console.error(`ERROR: Architecture doc not found: ${ARCH_DOC}`);
    process.exit(1);
  }

  const content = fs.readFileSync(ARCH_DOC, "utf8");
  const paths = extractPaths(content);

  if (paths.length === 0) {
    console.error("ERROR: No file paths found in Module Map table.");
    process.exit(1);
  }

  let allPassed = true;
  console.log(`\nValidating ${paths.length} path(s) from ai-track-docs/architecture.md:\n`);

  for (const rel of paths) {
    const abs = path.join(REPO_ROOT, rel);
    const exists = fs.existsSync(abs);
    const icon = exists ? "✓" : "✗";
    console.log(`  ${icon}  ${rel}`);
    if (!exists) allPassed = false;
  }

  console.log();
  if (allPassed) {
    console.log("All paths verified. Architecture doc is valid.\n");
    process.exit(0);
  } else {
    console.error("FAILED: One or more paths do not exist. Update architecture.md.\n");
    process.exit(1);
  }
}

main();
