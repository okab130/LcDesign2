# LC自動倉庫モックサーバ

LC自動倉庫システムのAPIをシミュレートするモックサーバです。開発・テスト環境で本システムと連携してテストを行うために使用します。

**注意**: このモックサーバは開発テスト環境用です。認証なし、HTTP通信で動作します。

## 機能

- 在庫情報取得API（認証なし）
- 出庫依頼送信API（認証なし）
- テストデータ管理API（在庫追加、クリア、リセット）
- エラーシミュレーション（タイムアウト、サーバーエラー等）
- 手動Webhook送信（出庫実績を本システムへ送信）

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数設定

`.env.example`を`.env`にコピーして必要に応じて編集：

```bash
cp .env.example .env
```

### 3. モックサーバ起動

```bash
python app.py
```

または

```bash
flask run --host=0.0.0.0 --port=5001
```

サーバは`http://localhost:5001`で起動します。

## API一覧

### LC倉庫API（認証なし）

#### 在庫情報取得
```
GET /api/v1/inventory
```

#### 出庫依頼送信
```
POST /api/v1/shipment-requests
Content-Type: application/json
```

リクエスト:
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
        }
      ]
    }
  ]
}
```

### 管理API

#### 在庫データ追加
```
POST /api/v1/admin/inventory
```

#### 在庫データクリア
```
DELETE /api/v1/admin/inventory
```

#### 在庫データリセット
```
POST /api/v1/admin/inventory/reset
```

#### エラーモード設定
```
POST /api/v1/admin/error-mode
```

リクエスト:
```json
{
  "endpoint": "/api/v1/inventory",
  "error_type": "timeout"
}
```

エラータイプ:
- `timeout`: タイムアウトシミュレーション
- `server_error`: 500エラー
- `insufficient_inventory`: 在庫不足エラー

#### エラーモードクリア
```
DELETE /api/v1/admin/error-mode
```

#### 手動Webhook送信
```
POST /api/v1/admin/send-webhook
```

リクエスト:
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

## テスト例

### Pythonでのテスト

```python
import requests

# 1. 在庫情報取得（認証なし）
inventory_response = requests.get(
    "http://localhost:5001/api/v1/inventory"
)
print(inventory_response.json())

# 2. 出庫依頼送信（認証なし）
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
print(shipment_response.json())

# 3. 出庫実績Webhook送信（手動）
webhook_response = requests.post(
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
print(webhook_response.json())
```

### curlでのテスト

```bash
# 在庫情報取得（認証なし）
curl -X GET http://localhost:5001/api/v1/inventory

# 出庫依頼送信（認証なし）
curl -X POST http://localhost:5001/api/v1/shipment-requests \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## エラーシミュレーション

### タイムアウトエラー

```python
# タイムアウトモード設定
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

## データベース

SQLiteデータベース（`mock_data.db`）に以下のテーブルが作成されます：

- `inventories`: 在庫データ
- `shipment_requests`: 出庫依頼データ
- `error_modes`: エラーモード設定

データベースファイルを削除すると、次回起動時にデフォルトデータで初期化されます。

## トラブルシューティング

### ポートが既に使用されている

別のアプリケーションがポート5001を使用している場合、`.env`ファイルで別のポートを指定してください：

```
MOCK_SERVER_PORT=5002
```

### データベースエラー

データベースファイルを削除して再起動：

```bash
rm mock_data.db
python app.py
```

## 本番環境への移行について

このモックサーバは開発テスト環境専用です。本番環境では以下の対応が必要です：

1. **HTTPS通信への変更**
2. **JWT認証の実装**
3. **APIエンドポイントURLの変更**
4. **セキュリティ強化**

## ライセンス

このモックサーバは開発・テスト目的でのみ使用してください。
