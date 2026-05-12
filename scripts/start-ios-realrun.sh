#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$PROJECT_DIR/main.py" || ! -x "$PROJECT_DIR/.venv/bin/python" ]]; then
    PROJECT_DIR="/home/butterfalls/iOSRealRun/iOSRealRun-cli-17"
fi

cd "$PROJECT_DIR"

echo "请保持 iPhone 已连接、已解锁，并已信任此电脑。"
sudo -v

# GNOME may grab iPhone as a camera and prevent usbmuxd from talking to lockdownd.
pkill -f "gvfsd-gphoto2" 2>/dev/null || true

if ! timeout 8 sudo systemctl restart usbmuxd; then
    sudo systemctl kill usbmuxd 2>/dev/null || true
    sudo systemctl reset-failed usbmuxd 2>/dev/null || true
    sudo systemctl start usbmuxd
fi

exec sudo "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/main.py"
