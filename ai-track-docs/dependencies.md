# Dependency Notes & Pinning Policy

Critical dependencies across all sub-projects, with pinning constraints and
upgrade guidance.  "Critical" means the build, tests, or course content breaks
without it.

---

## Python — `samples/book-app-project/`

**File:** `samples/book-app-project/pyproject.toml`

### Current state

```toml
[project]
requires-python = ">=3.10"
dependencies = ["pytest"]
```

`pytest` is currently unpinned; the venv installed **9.0.3** during local setup
(2026-05-05).

### Proposed constraints

```toml
[project]
requires-python = ">=3.10,<3.14"
dependencies = ["pytest>=9.0,<10"]
```

| Constraint | Rationale |
|------------|-----------|
| `pytest>=9.0,<10` | 9.x is the currently installed generation; `<10` blocks a future major that may break plugin APIs or fixture semantics without an explicit review. |
| `requires-python <3.14` | Caps at the next unreleased minor so the course is tested on a known interpreter before students hit it. Remove this cap once CI passes on 3.13+. |

### Dependency inventory

| Package | Role | Criticality | Upgrade risk |
|---------|------|-------------|-------------|
| Python runtime | Language interpreter | **Critical** | Minor upgrades safe; major (3.x → 4.x) requires full review |
| `pytest` | Test runner for all exercises | **Critical** | Minor upgrades safe; major upgrade needs fixture/plugin audit |

### Policy

- Pin to `>=current_major.minor,<next_major` for test tooling.
- No pinning needed for the stdlib (`json`, `dataclasses`, `typing`) — these ship with Python and have no separate version.
- Run `pip list --outdated` before each course release to catch drift.

---

## JavaScript — `samples/book-app-project-js/`

**File:** `samples/book-app-project-js/package.json`

### Current state

```json
{ "scripts": { "test": "node --test tests/test_books.js" } }
```

No `dependencies` or `devDependencies` declared.  The test runner is Node's
built-in `node:test` module (available since Node 18).

### Proposed constraints

Add an `engines` field to the existing `package.json`:

```json
"engines": { "node": ">=18 <24" }
```

| Constraint | Rationale |
|------------|-----------|
| `>=18` | `node:test` was stabilised in Node 18 LTS (minimum already documented in `build-test.md`). |
| `<24` | Caps at the next even-numbered LTS line so the course is vetted before students use an untested major. |

### Dependency inventory

| Dependency | Role | Criticality | Upgrade risk |
|------------|------|-------------|-------------|
| Node.js runtime | Interpreter + built-in test runner | **Critical** | Even-numbered LTS versions (18, 20, 22) are safe; odd (experimental) versions should not be used. |

### Policy

- No npm packages → no `package-lock.json` needed; nothing to audit.
- Verify `node --test` API compatibility when bumping the Node LTS.

---

## C# — `samples/book-app-project-cs/`

**File:** `samples/book-app-project-cs/Tests/BookApp.Tests.csproj`

### Current state (already pinned to exact versions)

| Package | Pinned version |
|---------|---------------|
| `Microsoft.NET.Test.Sdk` | 17.14.1 |
| `xunit` | 2.9.3 |
| `xunit.runner.visualstudio` | 3.1.4 |
| `coverlet.collector` | 6.0.4 |
| Target framework | `net10.0` |

### Proposed constraints

The `.csproj` already uses exact version pinning, which is the correct practice
for .NET test projects.  Proposed policy changes only:

| Constraint | Rationale |
|------------|-----------|
| Keep exact pins | Prevents silent behaviour changes across `dotnet restore` calls in different environments. |
| `net10.0` TFM | .NET 10 is an LTS release; do not change the TFM without a course chapter review. |
| Allow minor bumps for `xunit` | xunit 2.x → 3.x is a breaking migration; stay on 2.x until the course is updated. |

### Policy

- Update pins deliberately, one package at a time, after running `dotnet test`.
- Use `dotnet list package --outdated` to check for available updates before each release.
- Do **not** upgrade `xunit` to 3.x without updating Chapter 03 test examples.

---

## Course Tooling — repo root

**File:** `package.json`

No `dependencies` or `devDependencies` are declared.  Build scripts call
external tools (`python3`, `node`, `vhs`) that must be present in `PATH`.

### Proposed constraints

Add an `engines` field:

```json
"engines": {
  "node": ">=18",
  "npm":  ">=9"
}
```

| External tool | Minimum version | Source |
|---------------|----------------|--------|
| Python 3 | 3.10 | `build-test.md` |
| Node.js | 18 LTS | `build-test.md` |
| VHS | any current | `brew install vhs` — only needed for demo GIF generation |
| GitHub CLI (`gh`) | 2.40 | `build-test.md` |

### Policy

- External tools are not pinned (no lock file covers them); document minimums
  in `build-test.md` and `.devcontainer/devcontainer.json`.
- CI uses `npm run release:ci` which requires only Python 3 and Node; VHS is
  a local-only dependency.

---

## General Pinning Policy

| Principle | Detail |
|-----------|--------|
| **Floor, not ceiling for runtimes** | Use `>=min_version` for Python and Node so students on newer patch releases aren't blocked. |
| **Floor + major ceiling for test tooling** | `>=current_major.minor,<next_major` prevents accidental breaking upgrades in CI. |
| **Exact pins for .NET packages** | `dotnet restore` is deterministic with exact pins; avoids subtle cross-env differences. |
| **Review before major bumps** | Any `major` version bump (pytest 9→10, xunit 2→3, Node 18→20 LTS) requires a pass through `build-test.md` and affected chapter README files. |
| **Audit cadence** | Run `pip list --outdated` / `dotnet list package --outdated` before each course release. |
