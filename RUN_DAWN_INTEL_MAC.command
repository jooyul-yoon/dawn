#!/bin/bash

set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VENV_DIR=".venv"
VENV_PYTHON="$VENV_DIR/bin/python"

wait_before_close() {
    echo
    read -r -p "Press Return to close this window..." _
}

find_python() {
    local candidate
    for candidate in \
        "/usr/local/bin/python3.12" \
        "/opt/homebrew/bin/python3.12" \
        "python3.12" \
        "python3"
    do
        if command -v "$candidate" >/dev/null 2>&1 \
            && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)' >/dev/null 2>&1
        then
            PYTHON_COMMAND="$candidate"
            return 0
        fi
    done
    return 1
}

if [ ! -x "$VENV_PYTHON" ]; then
    echo "[Dawn Intel] Looking for Python 3.12 or newer..."
    if ! find_python; then
        echo
        echo "ERROR: Python 3.12 or newer was not found."
        echo "Install Python from https://www.python.org/downloads/"
        wait_before_close
        exit 1
    fi

    echo "[Dawn Intel] Creating the macOS environment..."
    if ! "$PYTHON_COMMAND" -m venv "$VENV_DIR"; then
        echo "ERROR: The Python environment could not be created."
        wait_before_close
        exit 1
    fi
fi

echo "[Dawn Intel] Starting History Cases..."
if ! "$VENV_PYTHON" -m history_quiz.play "$@"; then
    echo
    echo "ERROR: Dawn Intel stopped because of an error."
    echo "Read the message above, then try again."
    wait_before_close
    exit 1
fi

wait_before_close
