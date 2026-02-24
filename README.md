# a01
It extract hypertext file from zip file exported by notion, embed image file with base64, reduce width restriction and set padding instead.

```powershell
#!/bin/bash

# --- 設定項目 ---
REPO_URL="https://github.com/ユーザー名/リポジトリ名.git"
EXEC_CMD="python src/utils/" # 実行したいコマンド

# 1. URLからリポジトリ名（フォルダ名）を自動取得
# 例: https://github.com/user/my-tool.git -> my-tool
DIR_NAME=$(basename "$REPO_URL" .git)

# 2. クローン済みか確認して実行
if [ ! -d "$DIR_NAME" ]; then
    echo "--- [Info] リポジトリが見つかりません。クローンします... ---"
    git clone "$REPO_URL"
fi

cd "$DIR_NAME" || exit

echo "--- [Info] プログラムを実行します... ---"
$EXEC_CMD

# 3. 実行後にアップデートを確認
echo "--- [Info] アップデートを確認中... ---"
git fetch origin

# ローカルとリモートの差分があるかチェック
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  新しいアップデートがあります。"
    read -p "更新しますか？ (y/N): " yn
    case "$yn" in
        [Yy]* ) 
            git pull
            echo "--- [Success] 更新が完了しました。 ---"
            ;;
        * ) 
            echo "--- [Skip] 更新をスキップしました。 ---"
            ;;
    esac
else
    echo "--- [Check] すでに最新の状態です。 ---"
fi
```