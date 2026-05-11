#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$PROJECT_DIR/main.py" || ! -x "$PROJECT_DIR/.venv/bin/python" ]]; then
    PROJECT_DIR="/home/butterfalls/iOSRealRun/iOSRealRun-cli-17"
fi

cd "$PROJECT_DIR"

exec sudo "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/main.py"
