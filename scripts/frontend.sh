#!/usr/bin/env bash
set -Eeuo pipefail

cd "./frontend"

CMD="${FRONTEND_DEV_CMD:-npm run dev --host}"
echo "[frontend] 启动 Vite: $CMD"
exec $SHELL -c "$CMD"