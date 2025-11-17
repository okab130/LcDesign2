# LC自動倉庫出庫指示システム Web API/REST インターフェース仕様

## 1. 概要

### 1.1 認証方式
- **認証方式**: JWT（JSON Web Token）認証
- **認証ヘッダー**: Authorization: Bearer {JWTトークン}
- **アルゴリズム**: HS256
- **トークン有効期限**:
  - アクセストークン: 30分
  - リフレッシュトークン: 24時間

### 1.2 通信プロトコル
- **プロトコル**: HTTPS（TLS 1.2以上）
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8

### 1.3 エンドポイントURL
- **LC自動倉庫API**: https://lc-warehouse-api.example.com
- **本システムAPI**: https://shipment-system.example.com

### 1.4 タイムアウト設定
- 在庫情報取得: 30秒
- 出庫依頼送信: 60秒
- 出庫実績受信: 60秒

---

## 2. JWT認証トークン取得API

### 2.1 トークン取得（初回認証）

#### エンドポイント
```
POST https://lc-warehouse-api.example.com/api/v1/auth/token
POST https://shipment-system.example.com/api/v1/auth/token
```

#### リクエストヘッダー
```
Content-Type: application/json
```

#### リクエストボディ
```json
{
  "client_id": "shipment_system_client",
  "client_secret": "xxxxxxxxxxxxxxxxxxxxx"
}
```

#### レスポンス（成功時）
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "refresh_expires_in": 86400
}
```

#### レスポンス（失敗時）
```json
{
  "error": "invalid_client",
  "error_description": "Invalid client credentials"
}
```

#### ステータスコード
- 200: 成功
- 401: 認証失敗

---

### 2.2 トークンリフレッシュ

#### エンドポイント
```
POST https://lc-warehouse-api.example.com/api/v1/auth/refresh
POST https://shipment-system.example.com/api/v1/auth/refresh
```

#### リクエストヘッダー
```
Content-Type: application/json
```

#### リクエストボディ
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### レスポンス（成功時）
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

#### レスポンス（失敗時）
```json
{
  "error": "invalid_token",
  "error_description": "Refresh token is expired or invalid"
}
```

#### ステータスコード
- 200: 成功
- 401: トークン無効/期限切れ

---

## 3. LC自動倉庫側が提供するAPI

### 3.1 在庫情報取得API

#### 概要
LC自動倉庫の全在庫情報を取得するAPI。在庫照会画面で「最新化」ボタン押下時に呼び出される。

#### エンドポイント
```
GET https://lc-warehouse-api.example.com/api/v1/inventory
```

#### リクエストヘッダー
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
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

**認証エラー（401）**
```json
{
  "error": "unauthorized",
  "error_description": "Invalid or expired JWT token"
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
- 200: 成功
- 401: 認証エラー（トークン無効/期限切れ）
- 500: サーバーエラー
- 504: タイムアウト

---

### 3.2 出庫依頼送信API

#### 概要
複数拠点の出庫依頼をまとめて送信するAPI。LC倉庫担当が出庫依頼一覧画面で送信ボタン押下時に呼び出される。

#### エンドポイント
```
POST https://lc-warehouse-api.example.com/api/v1/shipment-requests
```

#### リクエストヘッダー
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
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

**認証エラー（401）**
```json
{
  "error": "unauthorized",
  "error_description": "Invalid or expired JWT token"
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
- 401: 認証エラー（トークン無効/期限切れ）
- 500: サーバーエラー
- 504: タイムアウト

---

## 4. 本システムが提供するAPI

### 4.1 出庫実績受信API（Webhook）

#### 概要
LC自動倉庫から出庫完了後即時に出庫実績を受信するWebhook API。LC側から本システムのエンドポイントを呼び出す。

#### エンドポイント
```
POST https://shipment-system.example.com/api/v1/shipment-results
```

#### リクエストヘッダー
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
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

**認証エラー（401）**
```json
{
  "status": "error",
  "error": "unauthorized",
  "message": "Invalid or expired JWT token"
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
- 401: 認証エラー（トークン無効/期限切れ）
- 500: サーバーエラー

#### 処理フロー
1. Webhookリクエスト受信
2. JWTトークン検証
3. リクエストボディのバリデーション
   - 必須項目チェック
   - データ型チェック
   - 商品コード存在チェック
   - 配送拠点コード存在チェック
   - 出庫依頼ID存在チェック（request_idがnullでない場合）
4. LcShipmentResultテーブルへINSERT
5. HTTPステータスコード200とレスポンスJSONを返却

---

## 5. エラーハンドリング

### 5.1 クライアント側（本システム）

#### 在庫情報取得・出庫依頼送信
- タイムアウト発生時: 画面にポップアップでエラー表示
- APIエラー発生時: エラーメッセージをポップアップ表示
- リトライ: なし（ユーザーが手動で再実行）

#### トークン有効期限切れ時
1. リフレッシュトークンを使用して新しいアクセストークンを自動取得
2. 取得成功: 元のAPIリクエストを再実行
3. 取得失敗: 再認証が必要な旨をポップアップ表示

### 5.2 サーバー側（本システム）

#### 出庫実績受信
- 認証エラー: HTTPステータスコード401を返却
- バリデーションエラー: HTTPステータスコード400を返却、エラー詳細をレスポンスボディに含める
- サーバーエラー: HTTPステータスコード500を返却
- エラー内容はアプリケーションログに出力（画面表示なし）

---

## 6. セキュリティ

### 6.1 HTTPS通信
- 本番環境: 正式なSSL/TLS証明書を使用
- 開発環境: 自己署名証明書使用可能
- TLS 1.2以上を使用
- 証明書検証を必須とする

### 6.2 JWTトークン管理
- シークレットキー: 環境変数で管理、ハードコード禁止
- アルゴリズム: HS256
- アクセストークン有効期限: 30分（短く設定）
- リフレッシュトークン有効期限: 24時間
- リフレッシュトークン: セキュアな保存（HTTPOnly Cookie推奨）

### 6.3 クライアント認証情報
- クライアントID: 環境変数で管理
- クライアントシークレット: 環境変数で管理、暗号化推奨
- ハードコード禁止

---

## 7. APIログ

### 7.1 ログ出力項目
- リクエスト日時
- エンドポイントURL
- HTTPメソッド
- リクエストヘッダー（Authorizationは除く）
- リクエストボディ
- レスポンスステータスコード
- レスポンスボディ
- 処理時間
- エラー内容（エラー時のみ）
- スタックトレース（エラー時のみ）

### 7.2 ログレベル
- INFO: 正常処理
- WARN: タイムアウト、リトライ
- ERROR: APIエラー、認証エラー、サーバーエラー

### 7.3 ログ保存
- アプリケーションログファイルに出力
- データベーステーブルには保存しない（InterfaceReceiveLog/InterfaceSendLogテーブルは廃止）

---

## 8. 実装例（Python/Django）

### 8.1 JWT認証取得

```python
import requests
import os
from datetime import datetime, timedelta

class JWTTokenManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
    def get_token(self):
        """アクセストークンを取得（期限切れの場合は自動リフレッシュ）"""
        if self.access_token and datetime.now() < self.token_expires_at:
            return self.access_token
            
        if self.refresh_token:
            return self._refresh_token()
        else:
            return self._authenticate()
    
    def _authenticate(self):
        """初回認証"""
        url = "https://lc-warehouse-api.example.com/api/v1/auth/token"
        payload = {
            "client_id": os.getenv("LC_API_CLIENT_ID"),
            "client_secret": os.getenv("LC_API_CLIENT_SECRET")
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
        
        return self.access_token
    
    def _refresh_token(self):
        """トークンリフレッシュ"""
        url = "https://lc-warehouse-api.example.com/api/v1/auth/refresh"
        payload = {
            "refresh_token": self.refresh_token
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 401:
            # リフレッシュトークンも期限切れ、再認証
            return self._authenticate()
        
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
        
        return self.access_token
```

### 8.2 在庫情報取得

```python
def get_inventory():
    """LC自動倉庫から在庫情報を取得"""
    token_manager = JWTTokenManager()
    token = token_manager.get_token()
    
    url = "https://lc-warehouse-api.example.com/api/v1/inventory"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=True)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("在庫情報取得がタイムアウトしました")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise Exception("認証エラー: トークンが無効または期限切れです")
        else:
            raise Exception(f"APIエラー: {e.response.text}")
```

### 8.3 出庫依頼送信

```python
def send_shipment_requests(requests_data):
    """LC自動倉庫へ出庫依頼を送信"""
    token_manager = JWTTokenManager()
    token = token_manager.get_token()
    
    url = "https://lc-warehouse-api.example.com/api/v1/shipment-requests"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "requests": requests_data
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60, verify=True)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("出庫依頼送信がタイムアウトしました")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise Exception("認証エラー: トークンが無効または期限切れです")
        elif e.response.status_code == 400:
            raise Exception(f"バリデーションエラー: {e.response.text}")
        else:
            raise Exception(f"APIエラー: {e.response.text}")
```

### 8.4 出庫実績受信（Django REST framework）

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class ShipmentResultWebhookView(APIView):
    """出庫実績受信Webhook"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
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

## 9. テスト

### 9.1 単体テスト
- 各APIエンドポイントごとに正常系・異常系テストを実施
- モックサーバーを使用してLC自動倉庫APIをシミュレート

### 9.2 結合テスト
- 本システムとLC自動倉庫の実際のAPI連携テスト
- 開発環境で実施

### 9.3 負荷テスト
- 同時アクセス数を想定した負荷テスト
- タイムアウト設定の妥当性確認

---

## 10. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2023-11-16 | 1.0 | 初版作成（APIキー認証からJWT認証へ変更、HTTPからHTTPSへ変更） |
