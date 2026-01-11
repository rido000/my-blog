#!/bin/bash
# 1. 确保进入脚本所在的目录 (防止工作目录不对)
cd "$(dirname "$0")"

# 2. 设置默认值 (方便手动测试)
# Alwaysdata 会自动注入 IP 和 PORT，手动运行时如果为空，则使用以下默认值
IP="${IP:-0.0.0.0}"
PORT="${PORT:-8100}"

# 3. 打印调试信息 (你会看到在 Logs 里)
echo "[DEBUG] Starting ForestNav..."
echo "[DEBUG] Environment IP: $IP"
echo "[DEBUG] Environment PORT: $PORT"
echo "[DEBUG] Current Dir: $(pwd)"

# 3. 使用绝对路径启动 Gunicorn
# 增加 --log-level debug 以便于查看详细错误
# 注意：Alwaysdata 的 IPv6 地址 (fd00...) 需要加上方括号才能被 Gunicorn 识别
if [[ "$IP" == *:* ]]; then
  BIND_ADDR="[$IP]:$PORT"
else
  BIND_ADDR="$IP:$PORT"
fi

echo "[DEBUG] Bind Address: $BIND_ADDR"
exec ./venv/bin/gunicorn app:app --bind $BIND_ADDR --workers 1 --log-level debug --error-logfile - --access-logfile -

