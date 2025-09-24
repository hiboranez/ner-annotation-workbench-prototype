#!/usr/bin/env bash
set -Eeuo pipefail

cd "./backend"

if [ "${SYNC_PARSE:-}" = "1" ]; then
  echo "[celery] SYNC_PARSE=1, 跳过 Celery"
  exit 0
fi

if ! command -v celery >/dev/null 2>&1; then
  echo "[celery] 未找到 celery 命令，退出"
  exit 1
fi

CONCURRENCY="${CELERY_CONCURRENCY:-1}"
echo "[celery] 启动 Celery worker 并发=${CONCURRENCY}"
exec celery -A config worker -l info -c "${CONCURRENCY}"
