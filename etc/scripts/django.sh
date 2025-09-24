#!/usr/bin/env bash
# 后端单独启动脚本

set -Eeuo pipefail

cd "./backend"

PYTHON="${PYTHON:-python}"
HOST="${DJANGO_HOST:-127.0.0.1}"
PORT="${DJANGO_PORT:-8000}"

echo "[backend] 使用解释器: $("$PYTHON" -c 'import sys;print(sys.executable)')"

echo "[backend] 迁移数据库(若需要)..."
$PYTHON manage.py migrate --noinput

# Redis 探测
REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
if python - <<EOF 2>/dev/null
import socket
s=socket.socket()
s.settimeout(0.5)
try:
    s.connect(("${REDIS_HOST}", int("${REDIS_PORT}")))
    print("ok")
except Exception:
    pass
EOF
then
  echo "[backend] 检测到 Redis (${REDIS_HOST}:${REDIS_PORT})，启用异步解析"
else
  echo "[backend] 未检测到 Redis，启用同步解析模式(SYNC_PARSE=1)"
  export SYNC_PARSE=1
fi

echo "[backend] 启动 Django runserver: ${HOST}:${PORT}"
echo "[backend] (Ctrl+C 退出)"
exec $PYTHON -W default manage.py runserver "${HOST}:${PORT}"
