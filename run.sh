#!/usr/bin/env bash
# ==============================================================================
# Virtual Chemistry Laboratory — Universal Launcher Script
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Determine best available Python interpreter with Tkinter support
PYTHON_CMD=""

if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python3.11 >/dev/null 2>&1; then
    PYTHON_CMD="python3.11"
elif command -v /opt/homebrew/bin/python3.11 >/dev/null 2>&1; then
    PYTHON_CMD="/opt/homebrew/bin/python3.11"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 was not found on your PATH."
    exit 1
fi

# 2. Check if running tests or launch GUI
if [ "$1" == "test" ] || [ "$1" == "--test" ]; then
    echo "Running Virtual Titration Laboratory Automated Test Suite..."
    export PYTHONPATH="$SCRIPT_DIR"
    $PYTHON_CMD -m pytest tests/ -v
    exit 0
fi

echo "Launching Virtual Chemistry Laboratory (HCl–NaOH Titration)..."
export PYTHONPATH="$SCRIPT_DIR"
exec $PYTHON_CMD main.py "$@"
