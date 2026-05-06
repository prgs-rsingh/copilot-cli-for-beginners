#!/usr/bin/env node
/**
 * gen-arch-diagram.js
 *
 * Generates an architecture diagram and module map for samples/book-app-project/.
 * Writes:
 *   ai-track-docs/architecture.md   — human-readable doc with Mermaid diagram
 *   ai-track-docs/.arch-manifest.json — machine-readable snapshot for change diffing
 *
 * If a manifest already exists, prints a change summary before overwriting it.
 *
 * Usage:
 *   node .github/scripts/gen-arch-diagram.js
 *   npm run gen:arch
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

// ── Configuration ────────────────────────────────────────────────────────────

const REPO_ROOT = path.resolve(__dirname, "../..");
const TARGET_DIR = path.join(REPO_ROOT, "samples/book-app-project");
const OUT_DIR = path.join(REPO_ROOT, "ai-track-docs");
const ARCH_DOC = path.join(OUT_DIR, "architecture.md");
const MANIFEST_FILE = path.join(OUT_DIR, ".arch-manifest.json");

// Module purpose descriptions (maintained here alongside the script)
const MODULE_PURPOSES = {
  "books.py": "Core domain — `Book` dataclass, `BookCollection` CRUD + JSON persistence",
  "book_app.py": "CLI entry point — interactive menu, delegates to `BookCollection` and `utils`",
  "utils.py": "UI helpers — menu display, `parse_year()`, `show_books()`, feature flag `BOOK_APP_STRICT_YEAR`",
  "logging_config.py": "Observability — `JSONFormatter`, `get_logger()`, stderr-only structured logging",
  "resilience.py": "Resilience — `retry_with_backoff` decorator factory, exponential backoff for I/O",
};

// ── Helpers ──────────────────────────────────────────────────────────────────

function sha256(str) {
  return crypto.createHash("sha256").update(str).digest("hex").slice(0, 12);
}

/**
 * Parse import statements from a Python source file.
 * Returns a list of local module names (those present in TARGET_DIR).
 */
function parseImports(src, localModules) {
  const edges = new Set();
  const lines = src.split("\n");
  for (const line of lines) {
    // "import X" or "from X import Y"
    const m1 = line.match(/^import\s+([\w.]+)/);
    const m2 = line.match(/^from\s+([\w.]+)\s+import/);
    const mod = (m1 || m2)?.[1]?.split(".")[0];
    if (mod && localModules.has(mod)) {
      edges.add(mod);
    }
  }
  return [...edges];
}

/**
 * Read all .py files (top-level only) from TARGET_DIR.
 */
function readModules() {
  const entries = fs.readdirSync(TARGET_DIR).filter((f) => f.endsWith(".py"));
  const localNames = new Set(entries.map((f) => f.replace(".py", "")));
  const modules = {};

  for (const file of entries) {
    const absPath = path.join(TARGET_DIR, file);
    const src = fs.readFileSync(absPath, "utf8");
    const lines = src.split("\n").length;
    const imports = parseImports(src, localNames);
    modules[file] = { lines, imports, hash: sha256(src) };
  }
  return modules;
}

// ── Change summary ───────────────────────────────────────────────────────────

function computeChangeSummary(prev, curr) {
  const prevFiles = new Set(Object.keys(prev.modules));
  const currFiles = new Set(Object.keys(curr));
  const changes = [];

  // Added files
  for (const f of currFiles) {
    if (!prevFiles.has(f)) changes.push(`  + ADDED:   ${f}`);
  }
  // Removed files
  for (const f of prevFiles) {
    if (!currFiles.has(f)) changes.push(`  - REMOVED: ${f}`);
  }
  // Changed files
  for (const f of currFiles) {
    if (!prevFiles.has(f)) continue;
    const p = prev.modules[f];
    const c = curr[f];
    if (p.hash !== c.hash) {
      const lineDelta = c.lines - p.lines;
      const sign = lineDelta >= 0 ? `+${lineDelta}` : `${lineDelta}`;
      const edgesBefore = (p.imports || []).sort().join(",");
      const edgesAfter = (c.imports || []).sort().join(",");
      const edgeNote = edgesBefore !== edgesAfter
        ? ` | imports: [${edgesBefore || "—"}] → [${edgesAfter || "—"}]`
        : "";
      changes.push(`  ~ CHANGED: ${f} (lines ${sign}${edgeNote})`);
    }
  }
  return changes;
}

// ── Mermaid diagram ──────────────────────────────────────────────────────────

function buildMermaid(modules) {
  const lines = ["flowchart LR"];
  const nodeId = (f) => f.replace(".py", "").replace(/_/g, "");

  // Node labels
  for (const file of Object.keys(modules)) {
    const id = nodeId(file);
    const label = file.replace(".py", "");
    lines.push(`  ${id}["${label}"]`);
  }

  // Edges (file → dependency)
  for (const [file, data] of Object.entries(modules)) {
    for (const dep of data.imports) {
      const depFile = dep + ".py";
      if (modules[depFile]) {
        lines.push(`  ${nodeId(file)} --> ${nodeId(depFile)}`);
      }
    }
  }
  return lines.join("\n");
}

// ── Module map table ─────────────────────────────────────────────────────────

function buildModuleTable(modules) {
  const rows = ["| File | Lines | Purpose | Imports |", "|---|---|---|---|"];
  for (const [file, data] of Object.entries(modules)) {
    const purpose = MODULE_PURPOSES[file] || "—";
    const imports = data.imports.length ? data.imports.map((i) => `\`${i}\``).join(", ") : "—";
    rows.push(`| \`${file}\` | ${data.lines} | ${purpose} | ${imports} |`);
  }
  return rows.join("\n");
}

// ── Main ─────────────────────────────────────────────────────────────────────

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const modules = readModules();

  // Load existing manifest if present and compute change summary
  let changeSummary = "First run — no previous manifest to diff against.";
  let prevGeneratedAt = null;
  if (fs.existsSync(MANIFEST_FILE)) {
    const prev = JSON.parse(fs.readFileSync(MANIFEST_FILE, "utf8"));
    prevGeneratedAt = prev.generatedAt;
    const changes = computeChangeSummary(prev, modules);
    if (changes.length === 0) {
      changeSummary = "No changes detected since last run.";
    } else {
      changeSummary = `${changes.length} change(s) since ${prevGeneratedAt}:\n${changes.join("\n")}`;
    }
  }

  console.log(`\n📐 Architecture diagram generator`);
  console.log(`   Target: ${path.relative(REPO_ROOT, TARGET_DIR)}`);
  console.log(`   Modules found: ${Object.keys(modules).length}\n`);
  console.log(`📋 Change summary:\n${changeSummary}\n`);

  const mermaid = buildMermaid(modules);
  const moduleTable = buildModuleTable(modules);
  const generatedAt = new Date().toISOString();
  const diagramHash = sha256(mermaid);

  // Write architecture.md
  const doc = `# Architecture — book-app-project

> Auto-generated by \`npm run gen:arch\` (.github/scripts/gen-arch-diagram.js).
> Re-run after changing any Python module in \`samples/book-app-project/\` to refresh.
>
> Last generated: ${generatedAt}
> Diagram hash: \`${diagramHash}\`

## Module Map

${moduleTable}

## Dependency Graph

\`\`\`mermaid
${mermaid}
\`\`\`

## Change Summary (vs previous run)

\`\`\`
${changeSummary}
\`\`\`

## Refresh Instructions

\`\`\`bash
# From repo root:
npm run gen:arch

# Verify the diagram hash changed after a module edit:
cat ai-track-docs/.arch-manifest.json | python3 -m json.tool | grep diagramHash
\`\`\`

## Rollback

To remove the generated artifacts:
\`\`\`bash
rm ai-track-docs/architecture.md ai-track-docs/.arch-manifest.json
\`\`\`
`;

  fs.writeFileSync(ARCH_DOC, doc);

  // Write manifest
  const manifest = {
    generatedAt,
    diagramHash,
    targetDir: path.relative(REPO_ROOT, TARGET_DIR),
    modules,
    changeSummary,
  };
  fs.writeFileSync(MANIFEST_FILE, JSON.stringify(manifest, null, 2));

  console.log(`✅ Written: ${path.relative(REPO_ROOT, ARCH_DOC)}`);
  console.log(`✅ Written: ${path.relative(REPO_ROOT, MANIFEST_FILE)}`);
  console.log(`   Diagram hash: ${diagramHash}`);
}

main();
