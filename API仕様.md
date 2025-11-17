# LC自動倉庫出庫指示システム REST API インターフェース仕様（開発テスト環境用）

## 1. 概要

### 1.1 認証方式
- **認証方式**: なし（開発テスト環境用）
- **注意**: 本番環境へのデプロイ前にJWT認証を実装する必要があります

### 1.2 通信プロトコル
- **プロトコル**: HTTP（開発テスト環境用）
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8
- **注意**: 本番環境ではHTTPS（TLS 1.2以上）を使用してください

### 1.3 エンドポイントURL
- **LC自動倉庫モックサーバ**: http://localhost:5001
- **本システム**: http://localhost:8000

### 1.4 タイムアウト設定
- 在庫情報取得: 30秒
- 出庫依頼送信: 60秒
- 出庫実績受信: 60秒

---

## 2. LC自動倉庫側が提供するAPI（開発テスト環境では認証なし）

### 2.1 在庫情報取得API

#### 概要
LC自動倉庫の全在庫情報を取得するAPI。在庫照会画面で「最新化」ボタン押下時に呼び出される。

#### エンドポイント
```
GET http://localhost:5001/api/v1/inventory
```

#### リクエストヘッダー
```
Accept: application/json
```

#### リクエストパラメータ
なし（全量取得）

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

#### レスポンスフィールド説明

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| inventories | Array | ○ | 在庫情報の配列 |
| inventories[].pallet_id | String | ○ | パレットID |
| inventories[].product_code | String | ○ | 商品コード |
| inventories[].location_code | String | ○ | 倉庫内ロケーションコード |
| inventories[].factory_code | String | ○ | 製造工場コード |
| inventories[].line_code | String | ○ | 製造ラインコード |
| inventories[].production_number | String | ○ | 製造番号 |
| inventories[].production_date | Date | ○ | 製造年月日（YYYY-MM-DD） |
| inventories[].expiry_date | Date | ○ | 賞味期限（YYYY-MM-DD） |
| inventories[].quantity | Integer | ○ | 数量（ケース数） |
| inventories[].entry_type | String | ○ | 入庫区分（AUTO: 自動、MANUAL: 手動） |
| inventories[].entry_datetime | DateTime | ○ | 入庫日時（ISO 8601形式） |
| total_count | Integer | ○ | 総在庫件数 |

#### エラーレスポンス

**サーバーエラー（500）**
```json
{
  "error": "internal_server_error",
  "error_description": "An unexpected error occurred"
}
```

#### ステータスコード
- 200: 成功
- 500: サーバーエラー
- 504: タイムアウト

---

### 2.2 出庫依頼送信API

#### 概要
複数拠点の出庫依頼をまとめて送信するAPI。LC倉庫担当が出庫依頼一覧画面で送信ボタン押下時に呼び出される。

#### エンドポイント
```
POST http://localhost:5001/api/v1/shipment-requests
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
    },
    {
      "request_id": "REQ-20231115-002",
      "base_code": "BASE002",
      "delivery_date": "2023-11-16",
      "details": [
        {
          "line_number": 1,
          "product_code": "PRD001",
          "quantity": 300
        }
      ]
    }
  ]
}
```

#### リクエストフィールド説明

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| requests | Array | ○ | 出庫依頼の配列 |
| requests[].request_id | String | ○ | 出庫依頼ID（本システムで採番） |
| requests[].base_code | String | ○ | 配送拠点コード |
| requests[].delivery_date | Date | ○ | 配送予定日（YYYY-MM-DD） |
| requests[].details | Array | ○ | 依頼明細の配列 |
| requests[].details[].line_number | Integer | ○ | 明細行番号 |
| requests[].details[].product_code | String | ○ | 商品コード |
| requests[].details[].quantity | Integer | ○ | 依頼数量（ケース数） |

#### レスポンス（成功時）
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

#### エラーレスポンス

**バリデーションエラー（400）**
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

**サーバーエラー（500）**
```json
{
  "error": "internal_server_error",
  "error_description": "An unexpected error occurred"
}
```

#### ステータスコード
- 200: 成功（一部失敗を含む。resultsを確認）
- 400: バリデーションエラー
- 500: サーバーエラー
- 504: タイムアウト

---

## 3. 本システムが提供するAPI（開発テスト環境では認証なし）

### 3.1 出庫実績受信API（Webhook）

#### 概要
LC自動倉庫から出庫完了後即時に出庫実績を受信するWebhook API。LC側から本システムのエンドポイントを呼び出す。

#### エンドポイント
```
POST http://localhost:8000/api/v1/shipment-results
```

#### リクエストヘッダー
```
Content-Type: application/json
```

#### リクエストボディ
```json
{
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
    },
    {
      "result_id": "RES-20231115-002",
      "request_id": null,
      "pallet_id": "PLT-20231115-002",
      "product_code": "PRD002",
      "quantity": 150,
      "shipment_type": "MANUAL",
      "shipment_datetime": "2023-11-15T15:00:00Z",
      "base_code": "BASE002",
      "location_code": "A-01-02",
      "factory_code": "F001",
      "line_code": "L002",
      "production_number": "20231115-002",
      "production_date": "2023-11-15",
      "expiry_date": "2024-11-15"
    }
  ]
}
```

#### リクエストフィールド説明

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| results | Array | ○ | 出庫実績の配列 |
| results[].result_id | String | ○ | 出庫実績ID（LC側で採番） |
| results[].request_id | String | - | 出庫依頼ID（自動出庫の場合のみ。手動出庫はnull） |
| results[].pallet_id | String | ○ | パレットID |
| results[].product_code | String | ○ | 商品コード |
| results[].quantity | Integer | ○ | 出庫数量（ケース数） |
| results[].shipment_type | String | ○ | 出庫区分（AUTO: 自動、MANUAL: 手動） |
| results[].shipment_datetime | DateTime | ○ | 出庫日時（ISO 8601形式） |
| results[].base_code | String | - | 配送拠点コード |
| results[].location_code | String | ○ | 出庫元ロケーションコード |
| results[].factory_code | String | ○ | 製造工場コード |
| results[].line_code | String | ○ | 製造ラインコード |
| results[].production_number | String | ○ | 製造番号 |
| results[].production_date | Date | ○ | 製造年月日（YYYY-MM-DD） |
| results[].expiry_date | Date | ○ | 賞味期限（YYYY-MM-DD） |

#### レスポンス（成功時）
```json
{
  "status": "success",
  "message": "Shipment results received successfully",
  "received_count": 2
}
```

#### エラーレスポンス

**バリデーションエラー（400）**
```json
{
  "status": "error",
  "error": "validation_error",
  "message": "Invalid request data",
  "errors": [
    {
      "field": "results[0].product_code",
      "message": "product_code is required"
    },
    {
      "field": "results[1].quantity",
      "message": "quantity must be positive integer"
    }
  ]
}
```

**サーバーエラー（500）**
```json
{
  "status": "error",
  "error": "internal_server_error",
  "message": "An unexpected error occurred"
}
```

#### ステータスコード
- 200: 成功
- 400: バリデーションエラー
- 500: サーバーエラー

#### 処理フロー
1. Webhookリクエスト受信
2. リクエストボディのバリデーション
   - 必須項目チェック
   - データ型チェック
   - 商品コード存在チェック
   - 配送拠点コード存在チェック
   - 出庫依頼ID存在チェック（request_idがnullでない場合）
3. LcShipmentResultテーブルへINSERT
4. HTTPステータスコード200とレスポンスJSONを返却

---

## 4. エラーハンドリング

### 4.1 クライアント側（本システム）

#### 在庫情報取得・出庫依頼送信
- タイムアウト発生時: 画面にポップアップでエラー表示
- APIエラー発生時: エラーメッセージをポップアップ表示
- リトライ: なし（ユーザーが手動で再実行）

### 4.2 サーバー側（本システム）

#### 出庫実績受信
- バリデーションエラー: HTTPステータスコード400を返却、エラー詳細をレスポンスボディに含める
- サーバーエラー: HTTPステータスコード500を返却
- エラー内容はアプリケーションログに出力（画面表示なし）

---

## 5. 本番環境への移行

### 5.1 必要な変更
1. **通信プロトコル**: HTTP → HTTPS（TLS 1.2以上）
2. **認証**: なし → JWT認証実装
3. **エンドポイントURL**: localhost → 本番サーバURL
4. **環境変数**: JWT_SECRET_KEY等の設定

### 5.2 JWT認証実装時の仕様
- **ライブラリ**: djangorestframework-simplejwt
- **アクセストークン有効期限**: 30分
- **リフレッシュトークン有効期限**: 24時間
- **アルゴリズム**: HS256
- **シークレットキー**: 環境変数で管理（ハードコード禁止）

---

## 6. 実装例（Python/Django）

### 6.1 在庫情報取得（開発テスト環境用）

```python
def get_inventory():
    """LC自動倉庫から在庫情報を取得（開発テスト環境用）"""
    url = "http://localhost:5001/api/v1/inventory"
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("在庫情報取得がタイムアウトしました")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"APIエラー: {e.response.text}")
```

### 6.2 出庫依頼送信（開発テスト環境用）

```python
def send_shipment_requests(requests_data):
    """LC自動倉庫へ出庫依頼を送信（開発テスト環境用）"""
    url = "http://localhost:5001/api/v1/shipment-requests"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "requests": requests_data
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("出庫依頼送信がタイムアウトしました")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(f"バリデーションエラー: {e.response.text}")
        else:
            raise Exception(f"APIエラー: {e.response.text}")
```

### 6.3 出庫実績受信（Django REST framework）（開発テスト環境用）

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ShipmentResultWebhookView(APIView):
    """出庫実績受信Webhook（開発テスト環境用・認証なし）"""
    
    def post(self, request):
        try:
            results = request.data.get('results', [])
            
            # バリデーション
            errors = self._validate_results(results)
            if errors:
                return Response({
                    "status": "error",
                    "error": "validation_error",
                    "message": "Invalid request data",
                    "errors": errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # データベースへ保存
            received_count = self._save_results(results)
            
            return Response({
                "status": "success",
                "message": "Shipment results received successfully",
                "received_count": received_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"出庫実績受信エラー: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "error": "internal_server_error",
                "message": "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _validate_results(self, results):
        """バリデーション"""
        errors = []
        # バリデーションロジック実装
        return errors
    
    def _save_results(self, results):
        """データベースへ保存"""
        # 保存ロジック実装
        return len(results)
```

---

## 7. テスト

### 7.1 単体テスト
- 各APIエンドポイントごとに正常系・異常系テストを実施
- モックサーバーを使用してLC自動倉庫APIをシミュレート

### 7.2 結合テスト
- 本システムとLC自動倉庫の実際のAPI連携テスト
- 開発環境で実施

### 7.3 負荷テスト
- 同時アクセス数を想定した負荷テスト
- タイムアウト設定の妥当性確認

---

## 8. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2023-11-16 | 1.0 | 初版作成（APIキー認証からJWT認証へ変更、HTTPからHTTPSへ変更） |
| 2025-11-17 | 1.1 | 開発テスト環境用に変更（JWT認証なし、HTTP通信） |
