#!/bin/bash

# スクリプトが存在するディレクトリを取得
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Python実行パスを自動で検出
PYTHON_EXEC=$(which python3)

# 実行するPythonスクリプト
TARGET_SCRIPT="$BASE_DIR/main.py"

# main.py を実行
if [ -f "$TARGET_SCRIPT" ]; then
    "$PYTHON_EXEC" "$TARGET_SCRIPT"
else
    echo "Error: main.py が見つかりません。スクリプトの配置を確認してください。"
    exit 0
fi
