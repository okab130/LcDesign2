# LC自動倉庫出庫指示システム データモデル設計

## 1. 商品マスタ (Product)

### テーブル用途
商品の基本情報を管理するマスタテーブル。LC倉庫担当が商品マスタ管理画面で登録・更新する。

| 英語項目名 | 日本語項目名 | 型 | 項目の用途 | キー情報 |
|-----------|-------------|-----|-----------|---------|
| product_code | 商品コード | VARCHAR(20) | 商品を一意に識別するコード | PK |
| product_name | 商品名 | VARCHAR(100) | 商品の名称（例：アルコーラ、アルコーヒー） | NOT NULL |
| pallet_case_quantity | パレット積載ケース数 | INTEGER | 1パレットあたりの標準ケース数（出庫依頼の単位チェックに使用） | NOT NULL |
| is_active | 有効フラグ | BOOLEAN | 取扱中か否か | NOT NULL, DEFAULT TRUE |
| created_at | 作成日時 | TIMESTAMP | レコード作成日時 | NOT NULL |
| updated_at | 更新日時 | TIMESTAMP | レコード更新日時 | NOT NULL |

---

## 2. 配送拠点マスタ (DeliveryBase)

### テーブル用途
配送拠点の基本情報を管理するマスタテーブル。別システムからCSV形式で毎日7:00に受信し、全量入れ替えする。

| 英語項目名 | 日本語項目名 | 型 | 項目の用途 | キー情報 |
|-----------|-------------|-----|-----------|---------|
| base_code | 拠点コード | VARCHAR(10) | 拠点を一意に識別するコード（30拠点） | PK |
| base_name | 拠点名 | VARCHAR(100) | 拠点の名称 | NOT NULL |
| created_at | 作成日時 | TIMESTAMP | レコード作成日時 | NOT NULL |
| updated_at | 更新日時 | TIMESTAMP | レコード更新日時 | NOT NULL |

---

## 3. ユーザーマスタ (User)

### テーブル用途
システム利用者の情報を管理するマスタテーブル。情報システム部門の管理者がユーザー管理画面で登録・更新する。

| 英語項目名 | 日本語項目名 | 型 | 項目の用途 | キー情報 |
|-----------|-------------|-----|-----------|---------|
| user_id | ユーザーID | VARCHAR(50) | ログインIDとして使用 | PK |
| password | パスワード | VARCHAR(255) | ハッシュ化されたパスワード | NOT NULL |
| user_name | ユーザー名 | VARCHAR(100) | ユーザーの氏名 | NOT NULL |
| user_type | ユーザー区分 | VARCHAR(20) | ユーザーの種類（拠点倉庫担当、LC倉庫担当、管理者） | NOT NULL |
| base_code | 所属拠点コード | VARCHAR(10) | 所属する配送拠点（拠点倉庫担当のみ。LC倉庫担当・管理者はNULL） | FK (DeliveryBase) |
| is_active | 有効フラグ | BOOLEAN | 利用可否 | NOT NULL, DEFAULT TRUE |
| created_at | 作成日時 | TIMESTAMP | レコード作成日時 | NOT NULL |
| updated_at | 更新日時 | TIMESTAMP | レコード更新日時 | NOT NULL |

### インデックス
- idx_user_type (user_type)
- idx_user_base (base_code)

---

## 4. LC在庫テーブル (削除)

### 変更内容
REST API化に伴い、在庫情報はデータベースに保存せず、在庫照会画面で都度LC自動倉庫のREST APIから取得して画面表示するため、本テーブルは削除する。

---

## 5. LC出庫依頼テーブル (LcShipmentRequest)

### テーブル用途
配送拠点への出庫依頼情報を管理するテーブル。拠点倉庫担当が登録、LC倉庫担当が修正・送信する。

| 英語項目名 | 日本語項目名 | 型 | 項目の用途 | キー情報 |
|-----------|-------------|-----|-----------|---------|
| request_id | 出庫依頼ID | VARCHAR(30) | 出庫依頼を一意に識別するID | PK |
| base_code | 配送拠点コード | VARCHAR(10) | 配送先の拠点 | FK (DeliveryBase), NOT NULL |
| request_date | 依頼登録日 | DATE | 出庫依頼を登録した日付 | NOT NULL |
| delivery_date | 配送予定日 | DATE | 配送拠点への配送予定日（=出庫日）。登録日の翌営業日（土日除く）を自動設定 | NOT NULL |
| request_status | 依頼ステータス | VARCHAR(20) | 依頼の状態（作成済、送信済、エラー）。送信完了=完了 | NOT NULL |
| total_quantity | 合計数量 | INTEGER | 依頼全体の合計ケース数 | NOT NULL |
| note | 備考 | TEXT | 特記事項 | |
| requested_by | 依頼者 | VARCHAR(50) | 依頼を作成したユーザーID | FK (User), NOT NULL |
| requested_at | 依頼作成日時 | TIMESTAMP | 依頼作成日時 | NOT NULL |
| sent_by | 送信者 | VARCHAR(50) | 送信したLC倉庫担当のユーザーID | FK (User) |
| sent_at | 送信日時 | TIMESTAMP | LC倉庫への送信日時 | |
| created_at | 作成日時 | TIMESTAMP | レコード作成日時 | NOT NULL |
| updated_at | 更新日時 | TIMESTAMP | レコード更新日時 | NOT NULL |

### インデックス
- idx_request_status (request_status)
- idx_request_base_date (base_code, delivery_date)
- idx_request_date (request_date)

---

## 6. LC出庫依頼明細テーブル (LcShipmentRequestDetail)

### テーブル用途
出庫依頼の明細（商品単位）を管理するテーブル。1依頼に複数商品、1商品に複数パレット可能。

| 英語項目名 | 日本語項目名 | 型 | 項目の用途 | キー情報 |
|-----------|-------------|-----|-----------|---------|
| detail_id | 明細ID | BIGINT | 明細を一意に識別するID | PK (AUTO_INCREMENT) |
| request_id | 出庫依頼ID | VARCHAR(30) | 親の出庫依頼 | FK (LcShipmentRequest), NOT NULL |
| line_number | 明細行番号 | INTEGER | 依頼内での明細順序 | NOT NULL |
| product_code | 商品コード | VARCHAR(20) | 出庫する商品 | FK (Product), NOT NULL |
| requested_quantity | 依頼数量 | INTEGER | 出庫を依頼するケース数。商品マスタのパレット積載ケース数の倍数であること | NOT NULL |
| created_at | 作成日時 | TIMESTAMP | レコード作成日時 | NOT NULL |
| updated_at | 更新日時 | TIMESTAMP | レコード更新日時 | NOT NULL |

### インデックス
- idx_detail_request (request_id, line_number)

---

## 7. LC出庫実績テーブル (LcShipmentResult)

### テーブル用途
LC自動倉庫から出庫完了後即時にCSV形式で受信した出庫実績情報を管理するテーブル。1日に複数回受信可能。出庫実績検索画面で全ユーザーが参照可能。

| 英語項目名 | 日本語項目名 | 型 | 項目の用途 | キー情報 |
|-----------|-------------|-----|-----------|---------|
| result_id | 出庫実績ID | VARCHAR(30) | 出庫実績を一意に識別するID | PK |
| request_id | 出庫依頼ID | VARCHAR(30) | 元の出庫依頼（自動出庫の場合のみ紐付く。手動出庫はNULL） | FK (LcShipmentRequest) |
| pallet_id | パレットID | VARCHAR(30) | 出庫されたパレット | NOT NULL |
| product_code | 商品コード | VARCHAR(20) | 出庫された商品 | NOT NULL |
| quantity | 出庫数量 | INTEGER | 実際に出庫されたケース数 | NOT NULL |
| shipment_type | 出庫区分 | VARCHAR(20) | 出庫方法（自動、手動）。手動は緊急出庫・廃棄など | NOT NULL |
| shipment_datetime | 出庫日時 | TIMESTAMP | LC倉庫から出庫された日時 | NOT NULL |
| base_code | 配送拠点コード | VARCHAR(10) | 配送先拠点 | FK (DeliveryBase) |
| location_code | 出庫元ロケーション | VARCHAR(20) | 倉庫内の出庫元位置 | |
| factory_code | 製造工場コード | VARCHAR(10) | 製造工場（検索・表示用） | |
| line_code | 製造ラインコード | VARCHAR(20) | 製造ライン（検索・表示用） | |
| production_number | 製造番号 | VARCHAR(30) | 製造ロット番号 | |
| production_date | 製造年月日 | DATE | 製造日 | |
| expiry_date | 賞味期限 | DATE | 賞味期限 | |
| received_at | 受信日時 | TIMESTAMP | 実績情報受信日時 | NOT NULL |
| created_at | 作成日時 | TIMESTAMP | レコード作成日時 | NOT NULL |
| updated_at | 更新日時 | TIMESTAMP | レコード更新日時 | NOT NULL |

### インデックス
- idx_result_request (request_id)
- idx_result_pallet (pallet_id)
- idx_result_shipment_date (shipment_datetime)
- idx_result_base_date (base_code, shipment_datetime)
- idx_result_product (product_code)
- idx_result_expiry (expiry_date)

---

## 8. インタフェース受信ログテーブル (削除)

### 変更内容
REST API化に伴い、APIログはアプリケーションログで管理するため、本テーブルは削除する。

---

## 9. インタフェース送信ログテーブル (削除)

### 変更内容
REST API化に伴い、APIログはアプリケーションログで管理するため、本テーブルは削除する。

---

## ER図（テーブル関連図）

```
[Product] 1 ----* [LcShipmentRequestDetail]
[Product] 1 ----* [LcShipmentResult]

[DeliveryBase] 1 ----* [User]
[DeliveryBase] 1 ----* [LcShipmentRequest]
[DeliveryBase] 1 ----* [LcShipmentResult]

[User] 1 ----* [LcShipmentRequest] (requested_by)
[User] 1 ----* [LcShipmentRequest] (sent_by)

[LcShipmentRequest] 1 ----* [LcShipmentRequestDetail]
[LcShipmentRequest] 1 ----0..* [LcShipmentResult]
```

### REST API化に伴う削除テーブル
- LcInventory（在庫情報はREST APIで都度取得、DB保存なし）
- InterfaceReceiveLog（APIログはアプリケーションログで管理）
- InterfaceSendLog（APIログはアプリケーションログで管理）

---

---

## データモデル設計の補足説明

### 1. マスタデータの管理方針
- **商品マスタ**: システム内で管理。LC倉庫担当が商品マスタ管理画面で登録・更新
- **配送拠点マスタ**: 別システムからCSV受信（毎日7:00、全量入れ替え）
- **ユーザーマスタ**: システム内で管理。情報システム部門の管理者がユーザー管理画面で登録・更新
- **製造工場・ラインマスタ**: 不要（在庫情報・出庫実績の項目としてのみ保持）

### 2. ステータス管理
- **依頼ステータス**: 作成済（拠点倉庫担当が登録） → 送信済（LC倉庫担当が送信完了） / エラー（送信失敗）
- **在庫ステータス・明細ステータス**: LC自動倉庫側で管理（本システムでは管理不要）

### 3. インタフェース仕様
- **在庫情報取得**: 在庫照会画面で「最新化」ボタン押下時、REST API（GET https://lc-warehouse-api.example.com/api/v1/inventory）で全量取得、DB保存なし
- **配送拠点マスタ受信**: 不定期、CSV形式、画面から手動取り込み、全量入れ替え
- **出庫依頼送信**: 画面操作で随時、REST API（POST https://lc-warehouse-api.example.com/api/v1/shipment-requests）、複数拠点一括送信可能
- **出庫実績受信**: 出庫完了後即時、Webhook（POST https://shipment-system.example.com/api/v1/shipment-results）、LC側から本システムAPIを呼び出し
- **認証方式**: JWT（JSON Web Token）認証、Authorizationヘッダー（Bearer {token}）
- **通信プロトコル**: HTTPS（TLS 1.2以上）
- **エラーハンドリング**: 
  - 在庫取得・出庫送信: 画面にポップアップでエラー表示（リトライなし）
  - 出庫実績受信: HTTPエラーレスポンス返却、ログ出力
  - 配送拠点マスタ取り込み: 画面にエラー表示

### 4. ユーザー権限
- **拠点倉庫担当**: 自拠点の出庫依頼登録・参照、在庫照会、出庫実績検索
- **LC倉庫担当**: 全拠点の出庫依頼参照・修正・送信、商品マスタ管理、在庫照会、出庫実績検索
- **管理者**: ユーザー管理のみ

### 5. 業務運用フロー
1. 拠点倉庫担当が18:00までに翌日配送分の出庫依頼を登録（ステータス: 作成済、在庫確認バリデーションなし）
2. LC倉庫担当が翌日、在庫照会画面で「最新化」ボタン押下し在庫状況を確認、必要に応じて数量調整
3. LC倉庫担当が出庫依頼をチェックボックスで選択（複数拠点可）し、REST API送信（ステータス: 送信済/エラー）
4. LC自動倉庫が自動で在庫引当・出庫処理を実施
5. 出庫完了後、LC自動倉庫から本システムのWebhook（POST /api/v1/shipment-results）へ出庫実績を即時送信
6. 手動出庫（緊急出庫、廃棄など）も出庫実績として受信（出庫依頼IDとの紐付けなし）

### 6. データ整合性
- 在庫情報はデータベースに保存しない
- 在庫照会画面で「最新化」ボタン押下時に、LC自動倉庫のREST APIから最新在庫を取得して画面表示
- 出庫依頼登録時の在庫確認バリデーションは不要

### 7. 配送予定日の自動計算
- 登録日（システム日付）の翌営業日を自動設定（土日のみ除外、祝日は考慮不要）
- 例: 金曜日登録 → 配送予定日は月曜日
- 18:00以降も登録可能（締め切りなし）

### 8. 出庫依頼数量のバリデーション
- 依頼数量は商品マスタのパレット積載ケース数の倍数であること
- 画面登録時にチェックし、倍数でない場合はエラー

### 9. トレーサビリティ
- パレット単位で製造工場、ライン、製造番号、製造年月日、賞味期限を追跡可能
- 出庫実績と依頼の紐付けにより、依頼→実績の追跡が可能（自動出庫のみ）
- 手動出庫は依頼との紐付けなし

### 10. インデックス設計
- 検索・参照パフォーマンスを考慮したインデックス設計
- 外部キー制約により、データ整合性を確保

### 11. REST API化に伴う変更点
1. **在庫データ**: LcInventoryテーブル削除、REST APIで都度取得
2. **インタフェースログ**: InterfaceReceiveLog/InterfaceSendLogテーブル削除、アプリケーションログで管理
3. **出庫依頼送信**: CSV → REST API、複数拠点一括送信可能
4. **出庫実績受信**: CSV → Webhook（本システムがAPIエンドポイント提供）
5. **配送拠点マスタ**: 定期バッチ廃止、手動取り込み
6. **エラーハンドリング**: 画面ポップアップ表示（在庫取得・出庫送信）
7. **認証方式**: APIキー認証 → JWT（JSON Web Token）認証
8. **通信プロトコル**: HTTP → HTTPS（TLS 1.2以上）
