#!/usr/bin/env bash
# 开发环境: 仅用 Daphne 启动后端 (Channels + WebSocket)，前端继续用 Vite。
# 使用: bash scripts/backend.sh
set -Eeuo pipefail

cd "$(dirname "$0")/../../backend"

PYTHON="${PYTHON:-python}"
HOST="${DJANGO_HOST:-127.0.0.1}"
PORT="${DJANGO_PORT:-8000}"

if ! command -v daphne >/dev/null 2>&1; then
  echo "[daphne_dev] 未找到 daphne，请先安装: pip install daphne"
  exit 1
fi

echo "[daphne_dev] Python解释器: $("$PYTHON" -c 'import sys;print(sys.executable)')"
echo "[daphne_dev] 应用迁移..."
$PYTHON manage.py migrate --noinput

# 探测 Redis (用于 Channels 与 Celery)
REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
if $PYTHON - <<EOF 2>/dev/null
import socket,os
s=socket.socket();s.settimeout(0.5)
try:
    s.connect(("${REDIS_HOST}", int("${REDIS_PORT}")))
    print("OK")
except:
    pass
EOF
then
  echo "[daphne_dev] Redis 已检测到: ${REDIS_HOST}:${REDIS_PORT}"
  echo "[daphne_dev] 异步解析开启 (Celery 可用时再运行: bash scripts/celery.sh)"
else
  echo "[daphne_dev] 未检测到 Redis，回退同步解析 (导出 SYNC_PARSE=1)"
  export SYNC_PARSE=1
fi

export DJANGO_SETTINGS_MODULE="config.settings"

echo "[daphne_dev] 启动 Daphne ${HOST}:${PORT}"
echo "[daphne_dev] 停止: Ctrl+C"
exec daphne -b "${HOST}" -p "${PORT}" config.asgi:application
