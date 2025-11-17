@echo off
echo === LC自動倉庫出庫指示システム セットアップスクリプト ===
echo.

REM 仮想環境の作成
echo 1. 仮想環境を作成しています...
python -m venv venv

REM 仮想環境の有効化
echo 2. 仮想環境を有効化しています...
call venv\Scripts\activate.bat

REM 依存パッケージのインストール
echo 3. 依存パッケージをインストールしています...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 環境変数ファイルのコピー
echo 4. 環境変数ファイルを作成しています...
if not exist .env (
    copy .env.example .env
    echo .envファイルを作成しました。データベース接続情報などを設定してください。
) else (
    echo .envファイルは既に存在します。
)

REM ログディレクトリの作成
echo 5. ログディレクトリを作成しています...
if not exist logs mkdir logs

REM マイグレーション
echo 6. データベースマイグレーションを実行しています...
python manage.py makemigrations
python manage.py migrate

REM 静的ファイルの収集
echo 7. 静的ファイルを収集しています...
python manage.py collectstatic --noinput

echo.
echo === セットアップ完了 ===
echo.
echo 次のステップ:
echo 1. .envファイルを編集してデータベース接続情報などを設定
echo 2. スーパーユーザーを作成: python manage.py createsuperuser
echo 3. 開発サーバーを起動: python manage.py runserver
echo.
pause
