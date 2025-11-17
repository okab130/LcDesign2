# API使用例

## 認証

### JWTトークン取得
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user001",
    "password": "password123"
  }'
```

レスポンス:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### トークン更新
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

## 商品マスタ

### 商品登録
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "P001",
    "product_name": "アルコーラ",
    "pallet_case_quantity": 100,
    "is_active": true
  }'
```

### 商品一覧取得
```bash
curl -X GET http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer {access_token}"
```

## 配送拠点マスタ

### CSV取り込み
```bash
curl -X POST http://localhost:8000/api/v1/delivery-bases/import_csv/ \
  -H "Authorization: Bearer {access_token}" \
  -F "file=@delivery_base.csv"
```

CSVフォーマット例（delivery_base.csv）:
```csv
拠点コード,拠点名
B001,東京配送センター
B002,大阪配送センター
B003,名古屋配送センター
```

## 出庫依頼

### 出庫依頼登録
```bash
curl -X POST http://localhost:8000/api/v1/shipment-requests/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "base_code": "B001",
    "note": "通常配送",
    "requested_by": "user001",
    "details": [
      {
        "line_number": 1,
        "product_code": "P001",
        "requested_quantity": 200
      },
      {
        "line_number": 2,
        "product_code": "P002",
        "requested_quantity": 150
      }
    ]
  }'
```

### 出庫依頼一覧取得
```bash
curl -X GET "http://localhost:8000/api/v1/shipment-requests/?request_status=CREATED&base_code=B001" \
  -H "Authorization: Bearer {access_token}"
```

### LC倉庫へ送信
```bash
curl -X POST http://localhost:8000/api/v1/shipment-requests/send_to_lc/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "request_ids": ["REQ20231117100000B001", "REQ20231117100100B002"]
  }'
```

### 在庫情報取得
```bash
curl -X GET http://localhost:8000/api/v1/shipment-requests/get_inventory/ \
  -H "Authorization: Bearer {access_token}"
```

## 出庫実績

### 出庫実績一覧取得
```bash
curl -X GET "http://localhost:8000/api/v1/shipment-results/?base_code=B001&shipment_type=AUTO" \
  -H "Authorization: Bearer {access_token}"
```

### Webhook受信（LC倉庫から）
```bash
curl -X POST http://localhost:8000/api/v1/shipment-results/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "results": [
      {
        "result_id": "RES20231117120000001",
        "request_id": "REQ20231117100000B001",
        "pallet_id": "PLT20231117001",
        "product_code": "P001",
        "quantity": 200,
        "shipment_type": "AUTO",
        "shipment_datetime": "2023-11-17T12:00:00Z",
        "base_code": "B001",
        "location_code": "A-01-01",
        "factory_code": "F001",
        "line_code": "L001",
        "production_number": "20231115001",
        "production_date": "2023-11-15",
        "expiry_date": "2024-05-15"
      }
    ]
  }'
```

## ユーザー管理

### ユーザー登録
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user001",
    "password": "password123",
    "user_name": "山田太郎",
    "user_type": "BASE_STAFF",
    "base_code": "B001",
    "is_active": true
  }'
```

### パスワード変更
```bash
curl -X POST http://localhost:8000/api/v1/users/user001/change_password/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "password123",
    "new_password": "newpassword456"
  }'
```

### ログイン中ユーザー情報取得
```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer {access_token}"
```

## フィルタリング・検索・並び替え

### 複数条件でフィルタリング
```bash
curl -X GET "http://localhost:8000/api/v1/shipment-requests/?request_status=SENT&delivery_date=2023-11-18&ordering=-created_at" \
  -H "Authorization: Bearer {access_token}"
```

### 検索
```bash
curl -X GET "http://localhost:8000/api/v1/products/?search=アルコーラ" \
  -H "Authorization: Bearer {access_token}"
```

### ページネーション
```bash
curl -X GET "http://localhost:8000/api/v1/shipment-results/?page=2&page_size=50" \
  -H "Authorization: Bearer {access_token}"
```
