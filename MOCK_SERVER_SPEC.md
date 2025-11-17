# LC自動倉庫モックサーバ仕様

## 1. 概要

### 1.1 目的
- LC自動倉庫システムの開発・テスト環境として、LC自動倉庫側APIをシミュレートするモックサーバを提供
- 本システム（出庫指示システム）の単体テスト・結合テストを実際のLC倉庫システムなしで実施可能にする
- 様々なテストシナリオ（正常系、異常系、エッジケース）を柔軟に実行可能にする

### 1.2 実装方式
- **フレームワーク**: Flask（軽量で迅速な開発が可能）
- **認証**: なし（開発テスト環境用）
- **データストア**: SQLite（永続化、データ保持）
- **通信プロトコル**: HTTP（開発テスト環境用）
- **起動方式**: スタンドアロンサーバとして起動、開発時は本システムと並行稼働
- **起動ポート**: 5001（本システムは8000）

### 1.3 対象API
1. 在庫情報取得API
2. 出庫依頼送信API
3. 手動Webhook送信API（管理用）

### 1.4 提供機能
- APIエンドポイントの完全な模倣（認証なしバージョン）
- テストデータの管理（在庫データ、出庫依頼データ）
- エラーシナリオのシミュレーション（タイムアウト、サーバーエラー等）
- 管理APIによるテストデータの動的操作

---

## 2. アーキテクチャ

### 2.1 ディレクトリ構成
```
lc_warehouse_mock_server/
├── app.py                      # Flaskアプリケーションメイン
├── config.py                   # 設定ファイル
├── database.py                 # SQLiteデータベース管理
├── requirements.txt            # 依存パッケージ
├── api/
│   ├── __init__.py
│   ├── inventory.py            # 在庫情報API
│   ├── shipment_requests.py    # 出庫依頼API
│   └── admin.py                # 管理API
├── utils/
│   ├── __init__.py
│   ├── validators.py           # バリデーション
│   └── error_simulator.py      # エラーシミュレーション
├── tests/
│   ├── __init__.py
│   ├── test_inventory.py
│   └── test_shipment_requests.py
└── README.md
```

### 2.2 技術スタック
- **Python**: 3.10以上
- **Flask**: 3.0以上
- **Flask-CORS**: 4.0以上（開発環境用）
- **pytest**: 7.4以上（モックサーバ自体のテスト用）
- **注意**: 認証不要のためPyJWTは使用しません

---

## 3. API仕様

### 3.1 在庫情報取得API

#### エンドポイント
```
GET /api/v1/inventory
```

#### リクエストヘッダー
```
Accept: application/json
```

#### レスポンス（成功時）
```json
{
  "inventories": [
    {
      "pallet_id": "PLT-20231115-001",
      "product_code": "PRD001",
      "location_code": "A-01-01",
      "factory_code": "F001",
      "line_code": "L001",
      "production_number": "20231115-001",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 100,
      "entry_type": "AUTO",
      "entry_datetime": "2023-11-15T08:30:00Z"
    },
    {
      "pallet_id": "PLT-20231115-002",
      "product_code": "PRD002",
      "location_code": "A-01-02",
      "factory_code": "F001",
      "line_code": "L002",
      "production_number": "20231115-002",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 150,
      "entry_type": "MANUAL",
      "entry_datetime": "2023-11-15T09:00:00Z"
    }
  ],
  "total_count": 2
}
```

#### レスポンス（エラー）
```json
{
  "error": "internal_server_error",
  "error_description": "An unexpected error occurred"
}
```

#### ステータスコード
- 200: 成功
- 500: サーバーエラー
- 504: タイムアウト（シミュレーション）

#### 動作仕様
- インメモリまたはJSONファイルから在庫データを取得
- 全量データを返却

---

### 3.2 出庫依頼送信API

#### エンドポイント
```
POST /api/v1/shipment-requests
```

#### リクエストヘッダー
```
Content-Type: application/json
Accept: application/json
```

#### リクエストボディ
```json
{
  "requests": [
    {
      "request_id": "REQ-20231115-001",
      "base_code": "BASE001",
      "delivery_date": "2023-11-16",
      "details": [
        {
          "line_number": 1,
          "product_code": "PRD001",
          "quantity": 200
        },
        {
          "line_number": 2,
          "product_code": "PRD002",
          "quantity": 100
        }
      ]
    }
  ]
}
```

#### レスポンス（成功時）
```json
{
  "results": [
    {
      "request_id": "REQ-20231115-001",
      "status": "success",
      "message": "Request accepted"
    }
  ]
}
```

#### レスポンス（一部失敗時）
```json
{
  "results": [
    {
      "request_id": "REQ-20231115-001",
      "status": "success",
      "message": "Request accepted"
    },
    {
      "request_id": "REQ-20231115-002",
      "status": "error",
      "error_code": "insufficient_inventory",
      "message": "Insufficient inventory for product PRD001"
    }
  ]
}
```

#### レスポンス（バリデーションエラー）
```json
{
  "error": "validation_error",
  "error_description": "Invalid request data",
  "errors": [
    {
      "field": "requests[0].details[0].quantity",
      "message": "Quantity must be a positive integer"
    }
  ]
}
```

#### ステータスコード
- 200: 成功（一部失敗含む）
- 400: バリデーションエラー
- 500: サーバーエラー
- 504: タイムアウト（シミュレーション）

#### 動作仕様
- リクエストボディをバリデーション
  - 必須項目チェック
  - データ型チェック
  - 数量が正の整数かチェック
- 在庫引当シミュレーション（在庫データと照合）
- 成功した依頼はインメモリまたはJSONファイルに保存

---

## 4. 管理API（テストデータ操作用）

### 4.1 在庫データ追加API

#### エンドポイント
```
POST /api/v1/admin/inventory
```

#### リクエストボディ
```json
{
  "pallet_id": "PLT-TEST-001",
  "product_code": "PRD001",
  "location_code": "A-01-01",
  "factory_code": "F001",
  "line_code": "L001",
  "production_number": "TEST-001",
  "production_date": "2023-11-15",
  "expiry_date": "2024-11-15",
  "quantity": 100,
  "entry_type": "AUTO",
  "entry_datetime": "2023-11-15T08:30:00Z"
}
```

#### レスポンス
```json
{
  "status": "success",
  "message": "Inventory added"
}
```

---

### 4.2 在庫データクリアAPI

#### エンドポイント
```
DELETE /api/v1/admin/inventory
```

#### レスポンス
```json
{
  "status": "success",
  "message": "All inventory data cleared"
}
```

---

### 4.3 在庫データ初期化API

#### エンドポイント
```
POST /api/v1/admin/inventory/reset
```

#### 動作
デフォルトのテストデータに初期化

#### レスポンス
```json
{
  "status": "success",
  "message": "Inventory data reset to default",
  "count": 10
}
```

---

### 4.4 エラーモード設定API

#### エンドポイント
```
POST /api/v1/admin/error-mode
```

#### リクエストボディ
```json
{
  "endpoint": "/api/v1/inventory",
  "error_type": "timeout",
  "enabled": true
}
```

#### エラータイプ
- `timeout`: タイムアウトシミュレーション
- `server_error`: 500エラー
- `insufficient_inventory`: 在庫不足エラー

#### レスポンス
```json
{
  "status": "success",
  "message": "Error mode set for /api/v1/inventory"
}
```

---

### 4.5 エラーモードクリアAPI

#### エンドポイント
```
DELETE /api/v1/admin/error-mode
```

#### レスポンス
```json
{
  "status": "success",
  "message": "All error modes cleared"
}
```

---

## 5. テストデータ

### 5.1 デフォルト在庫データ

```json
{
  "inventories": [
    {
      "pallet_id": "PLT-20231115-001",
      "product_code": "PRD001",
      "location_code": "A-01-01",
      "factory_code": "F001",
      "line_code": "L001",
      "production_number": "20231115-001",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 100,
      "entry_type": "AUTO",
      "entry_datetime": "2023-11-15T08:30:00Z"
    },
    {
      "pallet_id": "PLT-20231115-002",
      "product_code": "PRD002",
      "location_code": "A-01-02",
      "factory_code": "F001",
      "line_code": "L002",
      "production_number": "20231115-002",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 150,
      "entry_type": "MANUAL",
      "entry_datetime": "2023-11-15T09:00:00Z"
    },
    {
      "pallet_id": "PLT-20231115-003",
      "product_code": "PRD001",
      "location_code": "A-02-01",
      "factory_code": "F001",
      "line_code": "L001",
      "production_number": "20231115-003",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 200,
      "entry_type": "AUTO",
      "entry_datetime": "2023-11-15T10:00:00Z"
    },
    {
      "pallet_id": "PLT-20231115-004",
      "product_code": "PRD003",
      "location_code": "A-02-02",
      "factory_code": "F002",
      "line_code": "L003",
      "production_number": "20231115-004",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 120,
      "entry_type": "AUTO",
      "entry_datetime": "2023-11-15T11:00:00Z"
    },
    {
      "pallet_id": "PLT-20231115-005",
      "product_code": "PRD002",
      "location_code": "A-03-01",
      "factory_code": "F001",
      "line_code": "L002",
      "production_number": "20231115-005",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15",
      "quantity": 180,
      "entry_type": "AUTO",
      "entry_datetime": "2023-11-15T12:00:00Z"
    }
  ]
}
```

### 5.2 デフォルト認証情報

**注意**: 開発テスト環境では認証を使用しないため、認証情報は不要です。

---

## 6. エラーシミュレーション機能

### 6.1 タイムアウトシミュレーション
- 指定したエンドポイントで意図的に遅延を発生させる
- 設定: `{"endpoint": "/api/v1/inventory", "error_type": "timeout", "delay": 35}`
- 35秒待機後にタイムアウトエラーを返却

### 6.2 認証エラーシミュレーション
開発テスト環境では認証を使用しないため、このシミュレーションは不要です。

### 6.3 在庫不足シミュレーション
- 出庫依頼に対して在庫不足エラーを返却
- 特定商品コードに対して不足をシミュレート

### 6.4 サーバーエラーシミュレーション
- 500 Internal Server Errorを返却
- スタックトレースを含むエラーレスポンス

### 6.5 バリデーションエラーシミュレーション
- 不正なリクエストボディに対するエラーレスポンス
- フィールド単位のエラー情報を返却

---

## 7. 起動・設定

### 7.1 環境変数

```bash
# モックサーバ設定
MOCK_SERVER_HOST=0.0.0.0
MOCK_SERVER_PORT=5001
MOCK_SERVER_DEBUG=True

# CORS設定（開発環境用）
CORS_ENABLED=True
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# データ永続化（SQLite固定）
SQLITE_DB_PATH=./mock_data.db
```

### 7.2 起動方法

```bash
# 依存パッケージインストール
pip install -r requirements.txt

# モックサーバ起動
python app.py

# または
flask run --host=0.0.0.0 --port=5001
```

### 7.3 Docker対応

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  lc-mock-server:
    build: ./lc_warehouse_mock_server
    ports:
      - "5001:5001"
    environment:
      - MOCK_SERVER_PORT=5001
      - JWT_SECRET_KEY=mock_jwt_secret_key
      - SQLITE_DB_PATH=/app/data/mock_data.db
    volumes:
      - ./lc_warehouse_mock_server:/app
      - mock_data:/app/data

volumes:
  mock_data:
```

---

## 8. 使用例

### 8.1 基本的な使用フロー

```python
import requests

# 1. 在庫情報取得
inventory_response = requests.get(
    "http://localhost:5001/api/v1/inventory",
    headers={"Accept": "application/json"}
)
inventories = inventory_response.json()["inventories"]

# 2. 出庫依頼送信
shipment_response = requests.post(
    "http://localhost:5001/api/v1/shipment-requests",
    headers={"Content-Type": "application/json"},
    json={
        "requests": [
            {
                "request_id": "REQ-20231115-001",
                "base_code": "BASE001",
                "delivery_date": "2023-11-16",
                "details": [
                    {
                        "line_number": 1,
                        "product_code": "PRD001",
                        "quantity": 200
                    }
                ]
            }
        ]
    }
)
```

### 8.2 エラーシミュレーション使用例

```python
# タイムアウトエラーを設定
requests.post(
    "http://localhost:5001/api/v1/admin/error-mode",
    json={
        "endpoint": "/api/v1/inventory",
        "error_type": "timeout",
        "enabled": True
    }
)

# 在庫取得（タイムアウト発生）
try:
    response = requests.get(
        "http://localhost:5001/api/v1/inventory",
        timeout=30
    )
except requests.exceptions.Timeout:
    print("タイムアウトが発生しました")

# エラーモードクリア
requests.delete("http://localhost:5001/api/v1/admin/error-mode")
```

---

## 9. テストシナリオ

### 9.1 正常系テスト
1. 在庫情報取得
2. 出庫依頼送信（1拠点）
3. 出庫依頼送信（複数拠点一括）

### 9.2 異常系テスト
1. 不正なリクエストボディでの出庫依頼（400エラー）
2. 在庫不足時の出庫依頼（一部失敗）
3. タイムアウト発生時の処理
4. サーバーエラー（500）発生時の処理

### 9.3 エッジケーステスト
1. 在庫ゼロの商品への出庫依頼
2. 大量データ（1000件以上の在庫）取得
3. 複数拠点（30拠点）への一括出庫依頼
4. 同時並行での複数リクエスト

---

## 10. ログ出力

### 10.1 アクセスログ
```
2023-11-15 14:30:00 INFO GET /api/v1/inventory - 200 - 0.12s
2023-11-15 14:30:05 INFO POST /api/v1/shipment-requests - 200 - 0.08s
```

### 10.2 エラーログ
```
2023-11-15 14:31:00 ERROR GET /api/v1/inventory - 500 - Internal server error
2023-11-15 14:31:05 ERROR POST /api/v1/shipment-requests - 400 - Validation error: quantity must be positive
```

### 10.3 デバッグログ
```
2023-11-15 14:30:00 DEBUG Returning 5 inventory items
2023-11-15 14:30:05 DEBUG Shipment request accepted: REQ-20231115-001
```

---

## 11. 出庫実績Webhook送信（手動テスト手順）

### 11.1 手動Webhook送信API

モックサーバから本システムへ出庫実績をWebhook送信するテスト用API

#### エンドポイント
```
POST /api/v1/admin/send-webhook
```

#### リクエストボディ
```json
{
  "target_url": "http://localhost:8000/api/v1/shipment-results",
  "results": [
    {
      "result_id": "RES-20231115-001",
      "request_id": "REQ-20231115-001",
      "pallet_id": "PLT-20231115-001",
      "product_code": "PRD001",
      "quantity": 100,
      "shipment_type": "AUTO",
      "shipment_datetime": "2023-11-15T14:30:00Z",
      "base_code": "BASE001",
      "location_code": "A-01-01",
      "factory_code": "F001",
      "line_code": "L001",
      "production_number": "20231115-001",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15"
    }
  ]
}
```

#### レスポンス
```json
{
  "status": "success",
  "message": "Webhook sent successfully",
  "response_status": 200,
  "response_body": {
    "status": "success",
    "message": "Shipment results received successfully",
    "received_count": 1
  }
}
```

### 11.2 テスト手順

#### ステップ1: 本システムを起動
```bash
cd lc_warehouse_system
python manage.py runserver 8000
```

#### ステップ2: モックサーバを起動
```bash
cd lc_warehouse_mock_server
python app.py
```

#### ステップ3: 出庫依頼を送信（本システムから）
```python
import requests

# 出庫依頼送信
requests.post(
    "http://localhost:5001/api/v1/shipment-requests",
    headers={"Content-Type": "application/json"},
    json={
        "requests": [
            {
                "request_id": "REQ-20231115-001",
                "base_code": "BASE001",
                "delivery_date": "2023-11-16",
                "details": [
                    {
                        "line_number": 1,
                        "product_code": "PRD001",
                        "quantity": 200
                    }
                ]
            }
        ]
    }
)
```

#### ステップ4: 出庫実績をWebhook送信（手動）
```python
# モックサーバの管理APIを使用
requests.post(
    "http://localhost:5001/api/v1/admin/send-webhook",
    json={
        "target_url": "http://localhost:8000/api/v1/shipment-results",
        "results": [
            {
                "result_id": "RES-20231115-001",
                "request_id": "REQ-20231115-001",
                "pallet_id": "PLT-20231115-001",
                "product_code": "PRD001",
                "quantity": 100,
                "shipment_type": "AUTO",
                "shipment_datetime": "2023-11-15T14:30:00Z",
                "base_code": "BASE001",
                "location_code": "A-01-01",
                "factory_code": "F001",
                "line_code": "L001",
                "production_number": "20231115-001",
                "production_date": "2023-11-15",
                "expiry_date": "2024-11-15"
            }
        ]
    }
)
```

#### リクエストボディ
```json
{
  "target_url": "http://localhost:8000/api/v1/shipment-results",
  "results": [
    {
      "result_id": "RES-20231115-001",
      "request_id": "REQ-20231115-001",
      "pallet_id": "PLT-20231115-001",
      "product_code": "PRD001",
      "quantity": 100,
      "shipment_type": "AUTO",
      "shipment_datetime": "2023-11-15T14:30:00Z",
      "base_code": "BASE001",
      "location_code": "A-01-01",
      "factory_code": "F001",
      "line_code": "L001",
      "production_number": "20231115-001",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15"
    }
  ]
}
```

#### レスポンス
```json
{
  "status": "success",
  "message": "Webhook sent successfully",
  "response_status": 200,
  "response_body": {
    "status": "success",
    "message": "Shipment results received successfully",
    "received_count": 1
  }
}
```

### 11.2 テスト手順

#### ステップ1: 本システムを起動
```bash
cd lc_warehouse_system
python manage.py runserver 8000
```

#### ステップ2: モックサーバを起動
```bash
cd lc_warehouse_mock_server
python app.py
```

#### ステップ3: 出庫依頼を送信（本システムから）
```python
import requests

# トークン取得
auth_response = requests.post(
    "http://localhost:5001/api/v1/auth/token",
    json={
        "client_id": "shipment_system_client",
        "client_secret": "mock_secret_key_12345"
    }
)
access_token = auth_response.json()["access_token"]

# 出庫依頼送信
requests.post(
    "http://localhost:5001/api/v1/shipment-requests",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json={
        "requests": [
            {
                "request_id": "REQ-20231115-001",
                "base_code": "BASE001",
                "delivery_date": "2023-11-16",
                "details": [
                    {
                        "line_number": 1,
                        "product_code": "PRD001",
                        "quantity": 200
                    }
                ]
            }
        ]
    }
)
```

#### ステップ4: 出庫実績をWebhook送信（手動）
```python
# モックサーバの管理APIを使用
requests.post(
    "http://localhost:5001/api/v1/admin/send-webhook",
    json={
        "target_url": "http://localhost:8000/api/v1/shipment-results",
        "results": [
            {
                "result_id": "RES-20231115-001",
                "request_id": "REQ-20231115-001",
                "pallet_id": "PLT-20231115-001",
                "product_code": "PRD001",
                "quantity": 100,
                "shipment_type": "AUTO",
                "shipment_datetime": "2023-11-15T14:30:00Z",
                "base_code": "BASE001",
                "location_code": "A-01-01",
                "factory_code": "F001",
                "line_code": "L001",
                "production_number": "20231115-001",
                "production_date": "2023-11-15",
                "expiry_date": "2024-11-15"
            }
        ]
    }
)
```

#### ステップ5: 本システムで出庫実績を確認
- 出庫実績検索画面で確認
- または、データベースを直接確認
```bash
python manage.py shell
>>> from apps.shipment_results.models import LcShipmentResult
>>> LcShipmentResult.objects.all()
```

### 11.3 curlコマンドでのテスト例

```bash
# 出庫実績Webhook送信
curl -X POST http://localhost:5001/api/v1/admin/send-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "http://localhost:8000/api/v1/shipment-results",
    "results": [
      {
        "result_id": "RES-20231115-001",
        "request_id": "REQ-20231115-001",
        "pallet_id": "PLT-20231115-001",
        "product_code": "PRD001",
        "quantity": 100,
        "shipment_type": "AUTO",
        "shipment_datetime": "2023-11-15T14:30:00Z",
        "base_code": "BASE001",
        "location_code": "A-01-01",
        "factory_code": "F001",
        "line_code": "L001",
        "production_number": "20231115-001",
        "production_date": "2023-11-15",
        "expiry_date": "2024-11-15"
      }
    ]
  }'
```

---

## 12. 今後の拡張（オプション）

### 12.1 Web UI管理画面
- ブラウザからテストデータを管理
- エラーモードの設定・解除
- リクエスト/レスポンスの履歴表示

### 12.2 シナリオテスト機能
- 複数のAPIを順次呼び出すシナリオを定義
- テストケースの自動実行

### 12.3 負荷テスト対応
- 同時接続数のシミュレーション
- レスポンスタイム測定

---

## 13. 参考資料

- Flask公式ドキュメント: https://flask.palletsprojects.com/
- PyJWT公式ドキュメント: https://pyjwt.readthedocs.io/
- REST API設計ベストプラクティス
- LC自動倉庫出庫指示システム API仕様.md

---

## 14. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-11-17 | 1.0 | 初版作成 |
| 2025-11-17 | 1.1 | データストアをSQLite固定、HTTP固定、手動Webhook送信手順追加 |
| 2025-11-17 | 1.2 | 開発テスト環境用に変更（JWT認証削除、HTTP通信固定） |
