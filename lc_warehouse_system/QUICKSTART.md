# クイックスタートガイド（SQLite版）

PostgreSQLなしで、すぐに開発を始められます。

## 前提条件
- Python 3.10以上がインストールされていること

## 手順

### 1. Pythonのインストール確認
```bash
python --version
```

Python 3.10以上であることを確認してください。
インストールされていない場合：https://www.python.org/downloads/

### 2. プロジェクトディレクトリへ移動
```bash
cd lc_warehouse_system
```

### 3. 仮想環境の作成
```bash
python -m venv venv
```

### 4. 仮想環境の有効化
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 5. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 6. 環境変数ファイルの作成
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

`.env`ファイルはデフォルトでSQLiteを使用する設定になっています。

### 7. データベースのマイグレーション
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. スーパーユーザーの作成
```bash
python manage.py createsuperuser
```

以下の情報を入力：
- ユーザーID: admin（任意）
- ユーザー名: 管理者（任意）
- ユーザー区分: ADMIN
- パスワード: （任意、8文字以上推奨）

### 9. テストデータの投入（オプション）
```bash
python manage.py shell
```

シェルで以下を実行：
```python
from apps.products.models import Product
from apps.delivery_bases.models import DeliveryBase
from apps.users.models import User

# 商品マスタ
Product.objects.create(product_code="P001", product_name="アルコーラ", pallet_case_quantity=100)
Product.objects.create(product_code="P002", product_name="アルコーヒー", pallet_case_quantity=120)

# 配送拠点マスタ
DeliveryBase.objects.create(base_code="B001", base_name="東京配送センター")
DeliveryBase.objects.create(base_code="B002", base_name="大阪配送センター")

# LC倉庫担当ユーザー
lc_staff = User.objects.create(user_id="lc_staff", user_name="LC倉庫担当", user_type="LC_STAFF")
lc_staff.set_password("lc123")
lc_staff.save()

# 拠点倉庫担当ユーザー
tokyo_base = DeliveryBase.objects.get(base_code="B001")
base_staff = User.objects.create(user_id="base_staff", user_name="東京拠点担当", user_type="BASE_STAFF", base_code=tokyo_base)
base_staff.set_password("base123")
base_staff.save()

print("テストデータ投入完了")
exit()
```

### 10. 開発サーバーの起動
```bash
python manage.py runserver
```

### 11. 管理画面へのアクセス
ブラウザで http://localhost:8000/admin を開き、作成したスーパーユーザーでログイン

### 12. API動作確認

#### JWTトークン取得
```bash
curl -X POST http://localhost:8000/api/auth/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"lc_staff\", \"password\": \"lc123\"}"
```

レスポンスの`access`トークンをコピー

#### 商品一覧取得
```bash
curl -X GET http://localhost:8000/api/v1/products/ ^
  -H "Authorization: Bearer {上記のトークン}"
```

## トラブルシューティング

### Pythonが見つからない
- Pythonをインストール: https://www.python.org/downloads/
- インストール時に「Add Python to PATH」にチェック

### pipが見つからない
```bash
python -m ensurepip --upgrade
```

### マイグレーションエラー
```bash
python manage.py migrate --run-syncdb
```

### ポート8000が使用中
```bash
python manage.py runserver 8001
```

## 本番環境への移行

後でPostgreSQLに切り替える場合：
1. PostgreSQLをインストール
2. `.env`ファイルでDB_ENGINEをpostgresqlに変更
3. データベース情報を設定
4. マイグレーション再実行

## 参考ドキュメント
- SETUP.md - 詳細セットアップ手順
- API_EXAMPLES.md - API使用例
- PROJECT_SUMMARY.md - プロジェクト全体概要
