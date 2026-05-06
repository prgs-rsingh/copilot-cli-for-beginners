#!/usr/bin/env bash
# autofix.sh — Repeatable ruff autofix for samples/book-app-project/
#
# Applies safe, autofixable ruff rules across the entire project folder.
# Run this whenever new files are added or imports drift out of order.
#
# Rules autofixed:
#   I    — isort: sort and format import blocks
#   COM  — flake8-commas: add missing trailing commas
#   SIM  — flake8-simplify: merge nested `with` statements
#   PT   — flake8-pytest-style: @pytest.fixture() → @pytest.fixture
#   Q    — flake8-quotes: normalize quote style
#
# Unsafe rules (NOT applied here — require human review):
#   PERF403 — dict comprehension: structural change, verify output identity
#   TRY400  — logger.exception: changes traceback capture behavior
#   UP      — pyupgrade: may affect Python version compatibility
#
# Usage:
#   cd samples/book-app-project
#   bash autofix.sh
#
# To preview without writing (dry-run):
#   bash autofix.sh --diff
#
# Rollback:
#   git checkout HEAD -- .   (reverts all autofix changes in this folder)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RUFF=".venv/bin/ruff"

if [[ ! -x "$RUFF" ]]; then
    echo "ERROR: ruff not found at $RUFF"
    echo "Run: pip install -e '.[dev]' to install dev dependencies."
    exit 1
fi

# Accept --diff to preview without writing
EXTRA_ARGS=()
if [[ "${1:-}" == "--diff" ]]; then
    EXTRA_ARGS+=("--diff")
    echo "=== DRY RUN (--diff mode, no files written) ==="
else
    echo "=== Applying safe autofixes ==="
fi

"$RUFF" check . \
    --select I,COM,SIM,PT,Q \
    --fix \
    ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}

echo ""
echo "=== Running full check after autofix ==="
"$RUFF" check .

echo ""
echo "Done. Run .venv/bin/pytest to confirm no regressions."
