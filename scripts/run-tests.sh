#!/usr/bin/env bash
# run-tests.sh — run the Python sample app tests locally
#
# Usage:
#   bash scripts/run-tests.sh            # run all tests
#   bash scripts/run-tests.sh -v         # verbose output
#   bash scripts/run-tests.sh -k add     # filter by keyword
#
# Any extra arguments are forwarded directly to pytest.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR="$REPO_ROOT/samples/book-app-project"
VENV_DIR="$PROJECT_DIR/.venv"

# ── 1. Check Python ────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install Python 3.10+ and try again." >&2
  exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('%d.%d' % sys.version_info[:2])")
REQUIRED_MAJOR=3
REQUIRED_MINOR=10

ACTUAL_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
ACTUAL_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")

if [[ "$ACTUAL_MAJOR" -lt "$REQUIRED_MAJOR" ]] || \
   [[ "$ACTUAL_MAJOR" -eq "$REQUIRED_MAJOR" && "$ACTUAL_MINOR" -lt "$REQUIRED_MINOR" ]]; then
  echo "ERROR: Python $REQUIRED_MAJOR.$REQUIRED_MINOR+ required (found $PYTHON_VERSION)." >&2
  exit 1
fi

echo "Python $PYTHON_VERSION  ✓"

# ── 2. Create venv if missing ──────────────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment in $VENV_DIR …"
  python3 -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
PYTEST="$VENV_DIR/bin/pytest"

# ── 3. Install/upgrade pytest inside the venv ──────────────────────────────
echo "Installing dependencies …"
"$PIP" install --quiet "pytest>=9.0,<10"

# ── 4. Run pytest ──────────────────────────────────────────────────────────
echo ""
echo "Running tests in $PROJECT_DIR …"
echo ""
cd "$PROJECT_DIR"
"$PYTEST" tests/ "$@"
