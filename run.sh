#!/usr/bin/env bash
# AI Death Clock Launcher Script
# Sets library search path for Qt platform xcb cursor plugins and executes within project venv.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib/usr/lib/x86_64-linux-gnu"

if [ -d "$LIB_DIR" ]; then
    export LD_LIBRARY_PATH="$LIB_DIR:${LD_LIBRARY_PATH:-}"
fi

export DISPLAY="${DISPLAY:-:0.0}"

exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/main.py" "$@"
