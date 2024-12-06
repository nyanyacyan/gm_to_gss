#!/bin/bash

# スクリプトが存在するディレクトリを取得
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# requirements.txt のパス
REQUIREMENTS_FILE="$BASE_DIR/requirements.txt"

# Python 実行パスを確認
PYTHON_EXEC=$(which python3)


# requirements.txt が存在するか確認
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echo "依存関係をインストールしています..."
    "$PYTHON_EXEC" -m pip install --upgrade pip
    "$PYTHON_EXEC" -m pip install -r "$REQUIREMENTS_FILE"
    echo "インストールが完了しました！"
else
    echo "Error: requirements.txt が見つかりません。ファイルのパスを確認してください。"
    exit 1
fi
