#!/usr/bin/env bash
set +e

/home/butterfalls/iOSRealRun/iOSRealRun-cli-17/scripts/start-ios-realrun.sh
status=$?

echo
if [[ "$status" -eq 0 ]]; then
    echo "程序已退出。"
else
    echo "程序异常退出，退出码: $status"
fi

read -r -p "按 Enter 关闭窗口..."
exit "$status"
