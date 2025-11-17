# セットアップ完了確認

## ✅ 完了した作業

### 1. ドキュメント修正
- ✅ youken.md: 開発テスト環境用に変更（HTTP、認証なし、SQLite）
- ✅ API仕様.md: 開発テスト環境用に変更
- ✅ MOCK_SERVER_SPEC.md: 開発テスト環境用に変更
- ✅ lc_warehouse_system/README.md: 開発テスト環境用に変更

### 2. モックサーバ修正
- ✅ JWT認証削除
- ✅ requirements.txt: PyJWT削除
- ✅ config.py: JWT設定削除
- ✅ app.py: auth_bp削除
- ✅ api/inventory.py: @require_jwt_auth削除
- ✅ api/shipment_requests.py: @require_jwt_auth削除
- ✅ api/admin.py: JWTトークン生成削除
- ✅ auth/ディレクトリ削除
- ✅ api/auth.py削除

### 3. 本システム修正
- ✅ requirements.txt: djangorestframework-simplejwt、psycopg2-binary削除
- ✅ settings.py: JWT認証設定コメントアウト、AllowAny設定
- ✅ urls.py: JWT認証エンドポイントコメントアウト
- ✅ .env.example: 開発テスト環境用に変更

### 4. Python 3.13対応
- ✅ Django 5.0.0にアップグレード
- ✅ Pillow 12.0.0にアップグレード
- ✅ 依存パッケージインストール成功

### 5. データベース
- ✅ SQLite3マイグレーション完了
- ✅ db.sqlite3ファイル作成済み

## 次のステップ

### モックサーバ起動テスト

```bash
cd C:\Users\user\gh\LcDesign2\lc_warehouse_mock_server
python app.py
```

期待される出力:
```
Starting LC Warehouse Mock Server on 0.0.0.0:5001
Debug mode: True
CORS enabled: True
NOTE: Running in development mode - No authentication required
```

### 本システム起動テスト

別のターミナルで:
```bash
cd C:\Users\user\gh\LcDesign2\lc_warehouse_system
python manage.py runserver 8000
```

### 動作確認

#### 1. モックサーバヘルスチェック
```bash
curl http://localhost:5001/health
```

期待される出力:
```json
{"status":"healthy"}
```

#### 2. 在庫情報取得（認証なし）
```bash
curl http://localhost:5001/api/v1/inventory
```

#### 3. 本システムヘルスチェック
```bash
curl http://localhost:8000/admin/
```

## 設定ファイル確認

### モックサーバ (.env)
```
MOCK_SERVER_HOST=0.0.0.0
MOCK_SERVER_PORT=5001
MOCK_SERVER_DEBUG=True
CORS_ENABLED=True
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
SQLITE_DB_PATH=./mock_data.db
```

### 本システム (.env)
```
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
LC_WAREHOUSE_API_BASE_URL=http://localhost:5001/api/v1
SYSTEM_API_BASE_URL=http://localhost:8000/api/v1
SHARED_FOLDER_PATH=./shared_files/delivery_base
```

## トラブルシューティング

### ポート5001が使用中
```bash
# Windowsでポート使用状況確認
netstat -ano | findstr :5001

# プロセス終了
taskkill /PID <PID> /F
```

### ポート8000が使用中
```bash
# Windowsでポート使用状況確認
netstat -ano | findstr :8000

# プロセス終了
taskkill /PID <PID> /F
```

### データベースリセット
```bash
# モックサーバ
cd C:\Users\user\gh\LcDesign2\lc_warehouse_mock_server
del mock_data.db

# 本システム
cd C:\Users\user\gh\LcDesign2\lc_warehouse_system
del db.sqlite3
python manage.py migrate
```

## テスト手順

### 1. 初期データ投入

#### スーパーユーザー作成
```bash
cd C:\Users\user\gh\LcDesign2\lc_warehouse_system
python manage.py createsuperuser
```

**入力内容:**
- ユーザー名: `admin`
- メールアドレス: `admin@example.com`
- パスワード: `admin123`

#### 管理サイトログイン
```
URL: http://localhost:8000/admin/
ID: admin
パスワード: admin123
```

#### 初期マスターデータ登録

**商品マスタ:**
| 商品コード | 商品名 |
|-----------|--------|
| PROD001 | 商品A |
| PROD002 | 商品B |

**配送拠点マスタ:**
| 拠点コード | 拠点名 |
|-----------|--------|
| BASE001 | 東京拠点 |
| BASE002 | 大阪拠点 |

### 2. 出庫依頼登録テスト

#### 通常サイトログイン
```
URL: http://localhost:8000/
ID: admin
パスワード: admin123
```

#### 新規出庫依頼登録
1. メニューから「出庫依頼」をクリック
2. 「新規出庫依頼登録」ボタンをクリック
3. 以下の情報を入力:
   - 依頼日: 今日の日付
   - 依頼者: admin
   - 明細: 商品コード `PROD001`、数量 `10`
4. 「登録」ボタンをクリック

**期待結果:**
- ✅ 「登録が完了しました」メッセージ表示
- ✅ 出庫依頼一覧に新規データ表示
- ✅ ステータス: 未送信

### 3. LC自動倉庫送信テスト

#### 出庫依頼送信
1. 出庫依頼一覧で「詳細」ボタンをクリック
2. 詳細画面で「LC自動倉庫へ送信」ボタンをクリック

**期待結果:**
- ✅ 「送信が完了しました」メッセージ表示
- ✅ ステータス: 送信済み
- ✅ モックサーバのコンソールにPOSTリクエストログ表示

### 4. 出庫実績Webhook受信テスト

#### 手動Webhook送信
```bash
cd C:\Users\user\gh\LcDesign2
python test_webhook.py
```

**期待される出力:**
```
=== LC自動倉庫モックサーバへの出庫実績Webhook送信テスト ===

送信先URL: http://localhost:8000/api/v1/shipment-result/webhook/

送信データ:
{
  "results": [
    {
      "request_id": "REQ-001",
      "base_code": "BASE001",
      ...
    }
  ]
}

✅ ステータスコード: 201
✅ レスポンス:
{
  "message": "2件の出庫実績を受信しました。",
  "created_count": 2
}

🎉 出庫実績の送信に成功しました！
📋 画面で確認: http://localhost:8000/shipment-result/
```

#### 画面確認
```
URL: http://localhost:8000/shipment-result/
```

**期待結果:**
- ✅ 出庫実績が一覧表示される
- ✅ 2件のデータが登録されている
- ✅ 明細データも正しく表示される

### 5. エンドツーエンドテスト

#### 完全フロー確認
1. **出庫依頼登録** → 未送信ステータス
2. **LC自動倉庫送信** → 送信済みステータス
3. **モックサーバ処理** → 出庫実績Webhook送信（自動）
4. **出庫実績受信** → 実績データ登録
5. **画面確認** → 実績一覧表示

**注意事項:**
- モックサーバの自動Webhook送信機能は未実装のため、手動で `test_webhook.py` を実行
- 本番環境では、LC自動倉庫システムから自動的にWebhookが送信される

### 6. トラブルシューティング

#### 「出庫依頼データの取得に失敗しました」
- **原因:** ログインしていない
- **解決:** http://localhost:8000/ でログイン後、再度アクセス

#### 「登録に失敗しました: 商品が存在しません」
- **原因:** 商品マスタ未登録
- **解決:** 管理サイトで商品マスタを登録

#### 「LC自動倉庫APIへの送信に失敗しました」
- **原因:** モックサーバが起動していない
- **解決:** モックサーバを起動 `python app.py`

#### Webhook受信で「外部キー制約エラー」
- **原因:** `request_id`や`base_code`が存在しない
- **対処:** 開発環境では警告ログ出力のみで登録は継続される（NULL設定）

## 開発環境まとめ

| 項目 | 設定 |
|------|------|
| Python | 3.13.9 |
| Django | 5.0.0 |
| Flask | 3.0.0 |
| データベース | SQLite3 |
| 認証 | なし |
| 通信 | HTTP |
| モックサーバ | http://localhost:5001 |
| 本システム | http://localhost:8000 |
| 管理サイト | http://localhost:8000/admin/ |
| 通常サイト | http://localhost:8000/ |
| デフォルトユーザー | admin / admin123 |

## 本番環境への移行時チェックリスト

- [ ] requirements.txtにdjangorestframework-simplejwt追加
- [ ] requirements.txtにpsycopg2-binary追加
- [ ] settings.pyのJWT設定コメントアウト解除
- [ ] settings.pyのSIMPLE_JWT設定コメントアウト解除
- [ ] urls.pyのJWT認証エンドポイントコメントアウト解除
- [ ] .envのDB設定をPostgreSQLに変更
- [ ] .envのJWT_SECRET_KEY設定
- [ ] .envのAPIエンドポイントをHTTPSに変更
- [ ] ALLOWED_HOSTSに本番ドメイン追加
- [ ] DEBUG=False設定
- [ ] STATIC_ROOT設定と静的ファイル収集
- [ ] SSL/TLS証明書設定
