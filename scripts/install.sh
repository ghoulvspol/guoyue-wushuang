#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cat <<MSG

国乐无双安装完成。
启动：./scripts/run.sh
访问：http://127.0.0.1:8088
如识别模型项目不在默认位置，可设置：GUOYUE_RECOGNITION_DIR=/path/to/model-project ./scripts/run.sh
MSG
