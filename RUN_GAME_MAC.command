#!/bin/bash

set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VENV_DIR=".venv"
VENV_PYTHON="$VENV_DIR/bin/python"

wait_on_error() {
    echo
    read -r -p "Press Return to close this window..." _
    exit 1
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
    echo "[Dawn Tactics] Looking for Python 3.12 or newer..."
    if ! find_python; then
        echo
        echo "ERROR: Python 3.12 or newer was not found."
        echo "Install Python from https://www.python.org/downloads/"
        wait_on_error
    fi

    echo "[Dawn Tactics] Creating the macOS environment..."
    if ! "$PYTHON_COMMAND" -m venv "$VENV_DIR"; then
        echo "ERROR: The Python environment could not be created."
        wait_on_error
    fi
fi

if ! "$VENV_PYTHON" -c 'import dawn_tactics, pygame' >/dev/null 2>&1; then
    echo "[Dawn Tactics] Installing the game for the first launch..."
    echo "Internet access may be needed for a minute."
    if ! "$VENV_PYTHON" -m pip install -e .; then
        echo
        echo "ERROR: The game could not be installed."
        echo "Check the internet connection, then run this file again."
        wait_on_error
    fi
fi

echo "[Dawn Tactics] Starting game..."
if ! "$VENV_PYTHON" -m dawn_tactics "$@"; then
    echo
    echo "ERROR: The game stopped because of an error."
    echo "Read the message above for the variable or file that needs attention."
    wait_on_error
fi
