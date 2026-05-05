# System Overview

## Purpose

`ai-track-docs/` is the living technical reference for this repository. It records how the codebase is structured, how it is built and tested, and how AI-assisted workflows (GitHub Copilot CLI, agents, skills) fit into the development loop.

This document is the entry point. Start here before reading any other file in this directory.

---

## Repository at a Glance

| Item | Detail |
|------|--------|
| **Type** | Educational courseware (not a software product) |
| **Primary language** | Python 3.10+ |
| **Secondary languages** | C#, JavaScript |
| **Test framework** | pytest |
| **Package manager** | npm (course tooling), pip/pyproject.toml (samples) |
| **Primary sample app** | `samples/book-app-project/` |

---

## Directory Map

```
copilot-cli-for-beginners/
├── 00-07/                      # Chapter directories (analogy → concepts → hands-on → assignment → next)
├── samples/
│   ├── book-app-project/       # Primary Python sample used across all chapters
│   ├── book-app-project-cs/    # C# variant
│   ├── book-app-project-js/    # JavaScript variant
│   ├── book-app-buggy/         # Intentional bugs — do NOT fix
│   ├── buggy-code/             # Security-focused buggy code — do NOT fix
│   ├── agents/                 # .agent.md templates
│   ├── skills/                 # SKILL.md templates
│   └── mcp-configs/            # MCP server configuration examples
├── appendices/                 # Supplementary reference material
├── images/                     # Repo-root banners and diagrams
├── ai-track-docs/              # ← You are here
└── .copilot-track/
    └── crawl/                  # Crawl-phase working notes and prompt logs
```

---

## Key Conventions

- **Buggy sample files are intentional.** `samples/book-app-buggy/` and `samples/buggy-code/` contain deliberate bugs for exercises. Do not fix them.
- **Chapter structure is fixed.** Every chapter README follows: Real-World Analogy → Core Concepts → Hands-On Examples → Assignment → What's Next.
- **Kebab-case everywhere.** Session names, file names, and identifiers use kebab-case (e.g., `book-app-review`).
- **Flags:** `--flag=value` for valued flags, `--flag` for booleans.

---

## Languages, Entry Points & Test Approach

### Languages in use

| Language | Role | Key locations |
|----------|------|--------------|
| **Python 3.10+** | Primary sample app, GitHub Actions scripts | `samples/book-app-project/`, `.github/scripts/*.py` |
| **JavaScript (Node 18+)** | Secondary sample app, course build tooling | `samples/book-app-project-js/`, `.github/scripts/*.js`, `samples/src/` |
| **C# (.NET 10)** | Secondary sample app | `samples/book-app-project-cs/` |
| **Markdown** | All chapter content and documentation | `00-07/`, `appendices/`, `ai-track-docs/` |
| **JSON** | Data fixtures and configuration | `samples/*/data.json`, `mcp-configs/` |
| **TOML** | Python project metadata | `samples/book-app-project/pyproject.toml` |
| **VHS tape** | Demo GIF scripts | `***/images/*.tape` |
| **Mermaid** | Architecture diagrams | `ai-track-docs/architecture.mmd` |

### Entry points

| App | File | Run command |
|-----|------|------------|
| Python CLI (primary) | `samples/book-app-project/book_app.py` | `python book_app.py <command>` |
| JavaScript CLI | `samples/book-app-project-js/book_app.js` | `node book_app.js <command>` |
| C# CLI | `samples/book-app-project-cs/Program.cs` | `dotnet run -- <command>` |
| Course build | `package.json` root scripts | `npm run release` |

### Test approach

| Sample | Framework | Test location | Run command |
|--------|-----------|--------------|-------------|
| Python | **pytest** | `samples/book-app-project/tests/test_books.py` | `pytest tests/ -v` |
| JavaScript | **Node.js built-in** (`node:test`) | `samples/book-app-project-js/tests/test_books.js` | `npm test` |
| C# | **xUnit** + coverlet | `samples/book-app-project-cs/Tests/BookCollectionTests.cs` | `dotnet test Tests/` |

The Python suite has 6 tests covering the `BookCollection` service class (`add_book`, `mark_as_read`, `remove_book`, `find_book_by_title`, and error paths). `utils.py` and `book_app.py` are not unit-tested (I/O-heavy; verified manually or via integration).

---

## Low-Risk Modules for Modification

The three lowest-risk modules in the Python primary sample are:

| Module | Functions | Has tests? | External deps | Why low risk |
|--------|-----------|-----------|--------------|-------------|
| **`utils.py`** | 4 | No | None (stdlib only) | Pure formatting/I/O; isolated; changes are visually verifiable |
| **`books.py`** | 10 (BookCollection) | Yes — 6 tests | None (stdlib only) | Full pytest coverage catches regressions immediately |
| **`book_app.py`** | 8 | No (CLI entry point) | `books.py` only | Changes are local to argument dispatch; no data-layer risk |

### Recommended: `samples/book-app-project/books.py`

**Justification:** `books.py` is the core data and business-logic layer. It has:

- **Full pytest coverage** — 6 existing tests across `add_book`, `mark_as_read`, `remove_book`, `find_book_by_title`, and error paths. Any regression introduced by a change is caught immediately by running `pytest tests/ -v`.
- **Zero external dependencies** (only stdlib: `json`, `dataclasses`, `typing`) — no network calls, no third-party packages to install or mock.
- **Isolated from I/O** — it reads/writes a local `data.json` file; tests use a temp file via a pytest fixture, so nothing leaks between runs.
- **10 well-scoped methods** — each method does one thing, making it straightforward to add a new case or improve error handling without touching unrelated code.
- **Exercise-ready** — having an existing test suite means you can immediately practice the Arrange-Act-Assert workflow (via `prompt-write-tests.md`) and error-handling improvements (via `prompt-error-handling.md`) without writing test infrastructure from scratch.

Run tests with: `pytest samples/book-app-project/tests/ -v`

> **Note:** `samples/book-app-buggy/` and `samples/buggy-code/` are intentionally broken. Never choose a module from those directories.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [build-test.md](build-test.md) | How to build, run, and test the course and samples |
| [architecture.mmd](architecture.mmd) | Mermaid component diagram of the repo |
| [extending-books.md](extending-books.md) | Guide for adding fields/methods to `books.py` |
| [dependencies.md](dependencies.md) | Critical dependency inventory and pinning policy |
| [perf-baseline.md](perf-baseline.md) | Micro-benchmark baseline for `BookCollection` lookups |
| [logging.md](logging.md) | Structured log format, fields, and how to view logs |
| [.copilot-track/crawl/README.md](../.copilot-track/crawl/README.md) | Chain-PR workflow, evidence conventions, prompt usage |
| [AGENTS.md](../AGENTS.md) | Agent/skill authoring rules for this repo |
| [GLOSSARY.md](../GLOSSARY.md) | Definitions of all technical terms used in the course |
| [draft-pr-summary.md](draft-pr-summary.md) | PR draft with review focus, risks, rollback, and commit message improvements |
