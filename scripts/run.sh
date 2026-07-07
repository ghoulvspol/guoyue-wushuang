#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
if [ ! -d .venv ]; then
  echo "未找到 .venv，先执行 ./scripts/install.sh" >&2
  exit 1
fi
. .venv/bin/activate
HOST="${GUOYUE_HOST:-0.0.0.0}"
PORT="${GUOYUE_PORT:-8088}"
exec uvicorn app.main:app --host "$HOST" --port "$PORT"
