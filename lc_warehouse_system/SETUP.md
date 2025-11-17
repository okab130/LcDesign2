# LC自動倉庫出庫指示システム セットアップガイド

## 環境構築手順

### 1. Pythonのインストール
Python 3.10以上をインストールしてください。
https://www.python.org/downloads/

### 2. PostgreSQLのインストール
PostgreSQL 14以上をインストールしてください。
https://www.postgresql.org/download/

### 3. データベースの作成
```sql
CREATE DATABASE lc_warehouse_db;
CREATE USER lc_user WITH PASSWORD 'your_password';
ALTER ROLE lc_user SET client_encoding TO 'utf8';
ALTER ROLE lc_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lc_user SET timezone TO 'Asia/Tokyo';
GRANT ALL PRIVILEGES ON DATABASE lc_warehouse_db TO lc_user;
```

### 4. プロジェクトのセットアップ

#### 4.1 仮想環境の作成
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 4.2 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

#### 4.3 環境変数の設定
`.env.example`をコピーして`.env`を作成し、環境に応じて設定を変更してください。

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

`.env`ファイルを編集：
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=lc_warehouse_db
DB_USER=lc_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

#### 4.4 データベースマイグレーション
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 4.5 スーパーユーザーの作成
```bash
python manage.py createsuperuser
```

以下の情報を入力：
- ユーザーID: admin
- ユーザー名: 管理者
- ユーザー区分: ADMIN
- パスワード: (任意)

#### 4.6 初期データの投入（オプション）
```bash
python manage.py loaddata initial_data
```

### 5. 開発サーバーの起動
```bash
python manage.py runserver
```

アプリケーションは http://localhost:8000 で起動します。

### 6. 管理画面へのアクセス
http://localhost:8000/admin

作成したスーパーユーザーでログインしてください。

## API エンドポイント

### 認証
- `POST /api/auth/token/` - JWTトークン取得
- `POST /api/auth/token/refresh/` - JWTトークン更新

### 商品マスタ
- `GET /api/v1/products/` - 商品一覧
- `POST /api/v1/products/` - 商品登録
- `GET /api/v1/products/{id}/` - 商品詳細
- `PUT /api/v1/products/{id}/` - 商品更新
- `DELETE /api/v1/products/{id}/` - 商品削除

### 配送拠点マスタ
- `GET /api/v1/delivery-bases/` - 拠点一覧
- `POST /api/v1/delivery-bases/import_csv/` - CSV取り込み

### ユーザー管理
- `GET /api/v1/users/` - ユーザー一覧
- `POST /api/v1/users/` - ユーザー登録
- `GET /api/v1/users/me/` - ログイン中ユーザー情報
- `POST /api/v1/users/{id}/change_password/` - パスワード変更

### 出庫依頼
- `GET /api/v1/shipment-requests/` - 出庫依頼一覧
- `POST /api/v1/shipment-requests/` - 出庫依頼登録
- `PUT /api/v1/shipment-requests/{id}/` - 出庫依頼更新
- `DELETE /api/v1/shipment-requests/{id}/` - 出庫依頼削除
- `POST /api/v1/shipment-requests/send_to_lc/` - LC倉庫へ送信
- `GET /api/v1/shipment-requests/get_inventory/` - 在庫情報取得

### 出庫実績
- `GET /api/v1/shipment-results/` - 出庫実績一覧
- `POST /api/v1/shipment-results/webhook/` - Webhook受信（LC倉庫から）

## トラブルシューティング

### データベース接続エラー
- PostgreSQLサービスが起動しているか確認
- `.env`のデータベース設定が正しいか確認
- データベースユーザーの権限を確認

### マイグレーションエラー
```bash
python manage.py migrate --run-syncdb
```

### 静的ファイルが表示されない
```bash
python manage.py collectstatic
```

## 本番環境デプロイ

### 1. 環境変数の設定
```
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=production-secret-key
```

### 2. 静的ファイルの収集
```bash
python manage.py collectstatic
```

### 3. Gunicornの使用
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 4. Nginxの設定例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/lc_warehouse_system/staticfiles/;
    }

    location /media/ {
        alias /path/to/lc_warehouse_system/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## セキュリティ設定

### HTTPS化
本番環境では必ずHTTPS（TLS 1.2以上）を使用してください。

### JWT設定
- アクセストークン有効期限: 30分
- リフレッシュトークン有効期限: 24時間
- アルゴリズム: HS256

### CORS設定
必要なオリジンのみを`settings.py`の`CORS_ALLOWED_ORIGINS`に追加してください。
