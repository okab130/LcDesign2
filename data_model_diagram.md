# LC自動倉庫出庫指示システム データモデル図

## ERD（Entity Relationship Diagram）

```mermaid
erDiagram
    Product ||--o{ LcShipmentRequestDetail : "商品"
    Product ||--o{ LcShipmentResult : "商品"
    
    DeliveryBase ||--o{ User : "所属拠点"
    DeliveryBase ||--o{ LcShipmentRequest : "配送先"
    DeliveryBase ||--o{ LcShipmentResult : "配送先"
    
    User ||--o{ LcShipmentRequest : "依頼者(requested_by)"
    User ||--o{ LcShipmentRequest : "送信者(sent_by)"
    
    LcShipmentRequest ||--o{ LcShipmentRequestDetail : "明細"
    LcShipmentRequest ||--o{ LcShipmentResult : "出庫実績"

    Product {
        VARCHAR(20) product_code PK "商品コード"
        VARCHAR(100) product_name "商品名"
        INTEGER pallet_case_quantity "パレット積載ケース数"
        BOOLEAN is_active "有効フラグ"
        TIMESTAMP created_at "作成日時"
        TIMESTAMP updated_at "更新日時"
    }

    DeliveryBase {
        VARCHAR(10) base_code PK "拠点コード"
        VARCHAR(100) base_name "拠点名"
        TIMESTAMP created_at "作成日時"
        TIMESTAMP updated_at "更新日時"
    }

    User {
        VARCHAR(50) user_id PK "ユーザーID"
        VARCHAR(255) password "パスワード"
        VARCHAR(100) user_name "ユーザー名"
        VARCHAR(20) user_type "ユーザー区分"
        VARCHAR(10) base_code FK "所属拠点コード"
        BOOLEAN is_active "有効フラグ"
        TIMESTAMP created_at "作成日時"
        TIMESTAMP updated_at "更新日時"
    }

    LcShipmentRequest {
        VARCHAR(30) request_id PK "出庫依頼ID"
        VARCHAR(10) base_code FK "配送拠点コード"
        DATE request_date "依頼登録日"
        DATE delivery_date "配送予定日"
        VARCHAR(20) request_status "依頼ステータス"
        INTEGER total_quantity "合計数量"
        TEXT note "備考"
        VARCHAR(50) requested_by FK "依頼者"
        TIMESTAMP requested_at "依頼作成日時"
        VARCHAR(50) sent_by FK "送信者"
        TIMESTAMP sent_at "送信日時"
        TIMESTAMP created_at "作成日時"
        TIMESTAMP updated_at "更新日時"
    }

    LcShipmentRequestDetail {
        BIGINT detail_id PK "明細ID"
        VARCHAR(30) request_id FK "出庫依頼ID"
        INTEGER line_number "明細行番号"
        VARCHAR(20) product_code FK "商品コード"
        INTEGER requested_quantity "依頼数量"
        TIMESTAMP created_at "作成日時"
        TIMESTAMP updated_at "更新日時"
    }

    LcShipmentResult {
        VARCHAR(30) result_id PK "出庫実績ID"
        VARCHAR(30) request_id FK "出庫依頼ID"
        VARCHAR(30) pallet_id "パレットID"
        VARCHAR(20) product_code "商品コード"
        INTEGER quantity "出庫数量"
        VARCHAR(20) shipment_type "出庫区分"
        TIMESTAMP shipment_datetime "出庫日時"
        VARCHAR(10) base_code FK "配送拠点コード"
        VARCHAR(20) location_code "出庫元ロケーション"
        VARCHAR(10) factory_code "製造工場コード"
        VARCHAR(20) line_code "製造ラインコード"
        VARCHAR(30) production_number "製造番号"
        DATE production_date "製造年月日"
        DATE expiry_date "賞味期限"
        TIMESTAMP received_at "受信日時"
        TIMESTAMP created_at "作成日時"
        TIMESTAMP updated_at "更新日時"
    }
```

## テーブル一覧

### マスタテーブル
1. **Product（商品マスタ）** - 商品の基本情報を管理
2. **DeliveryBase（配送拠点マスタ）** - 配送拠点の基本情報を管理（CSV受信、全量入れ替え）
3. **User（ユーザーマスタ）** - システム利用者の情報を管理

### トランザクションテーブル
4. **LcShipmentRequest（LC出庫依頼テーブル）** - 配送拠点への出庫依頼情報を管理
5. **LcShipmentRequestDetail（LC出庫依頼明細テーブル）** - 出庫依頼の明細（商品単位）を管理
6. **LcShipmentResult（LC出庫実績テーブル）** - LC自動倉庫からの出庫実績情報を管理（Webhook受信）

## REST API化に伴う削除テーブル
- **LcInventory（在庫情報）** - REST APIで都度取得、DB保存なし
- **InterfaceReceiveLog（インタフェース受信ログ）** - アプリケーションログで管理
- **InterfaceSendLog（インタフェース送信ログ）** - アプリケーションログで管理

## 主要リレーションシップ

### マスタとトランザクション
- 商品マスタ → 出庫依頼明細（1:多）
- 商品マスタ → 出庫実績（1:多）
- 配送拠点マスタ → ユーザー（1:多）
- 配送拠点マスタ → 出庫依頼（1:多）
- 配送拠点マスタ → 出庫実績（1:多）

### ユーザーと出庫依頼
- ユーザー → 出庫依頼（依頼者）（1:多）
- ユーザー → 出庫依頼（送信者）（1:多）

### 出庫依頼と明細・実績
- 出庫依頼 → 出庫依頼明細（1:多）
- 出庫依頼 → 出庫実績（1:0以上）※手動出庫の場合は紐付けなし

## インデックス設計

### Product（商品マスタ）
- PK: product_code

### DeliveryBase（配送拠点マスタ）
- PK: base_code

### User（ユーザーマスタ）
- PK: user_id
- idx_user_type (user_type)
- idx_user_base (base_code)

### LcShipmentRequest（LC出庫依頼）
- PK: request_id
- idx_request_status (request_status)
- idx_request_base_date (base_code, delivery_date)
- idx_request_date (request_date)

### LcShipmentRequestDetail（LC出庫依頼明細）
- PK: detail_id
- idx_detail_request (request_id, line_number)

### LcShipmentResult（LC出庫実績）
- PK: result_id
- idx_result_request (request_id)
- idx_result_pallet (pallet_id)
- idx_result_shipment_date (shipment_datetime)
- idx_result_base_date (base_code, shipment_datetime)
- idx_result_product (product_code)
- idx_result_expiry (expiry_date)

## ステータス値

### request_status（依頼ステータス）
- `作成済` - 拠点倉庫担当が登録
- `送信済` - LC倉庫担当が送信完了（=完了）
- `エラー` - 送信失敗

### user_type（ユーザー区分）
- `拠点倉庫担当` - 所属拠点のみ操作可能
- `LC倉庫担当` - 全拠点のデータを操作可能
- `管理者` - ユーザー管理のみ

### shipment_type（出庫区分）
- `自動` - 出庫依頼に基づく自動出庫
- `手動` - 緊急出庫・廃棄など（依頼との紐付けなし）
