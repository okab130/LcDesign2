# LC自動倉庫出庫指示システム

## 概要
飲料製造・販売・配送業の企業向けLC（ロジスティクスセンター）自動倉庫の出庫指示機能を提供するWebシステムです。

## 主要機能
1. LC自動倉庫在庫受信・在庫更新
2. LC出庫依頼登録・送信
3. LC出庫実績格納
4. LC出庫実績検索
5. 在庫照会
6. 商品マスタ管理
7. ユーザー管理

## 技術スタック
- **バックエンド**: Django 4.2+
- **データベース**: PostgreSQL 14+
- **REST API**: Django REST framework
- **認証**: JWT (djangorestframework-simplejwt)
- **通信**: HTTPS (TLS 1.2+)

## 開発環境セットアップ

### 前提条件
- Python 3.10以上
- PostgreSQL 14以上
- Git

### インストール手順

1. リポジトリのクローン
```bash
git clone <repository_url>
cd lc_warehouse_system
```

2. 仮想環境の作成と有効化
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
`.env.example`をコピーして`.env`を作成し、必要な環境変数を設定
```bash
cp .env.example .env
```

5. データベースのセットアップ
```bash
python manage.py migrate
```

6. スーパーユーザーの作成
```bash
python manage.py createsuperuser
```

7. 開発サーバーの起動
```bash
python manage.py runserver
```

アプリケーションは http://localhost:8000 で起動します。

## プロジェクト構造
```
lc_warehouse_system/
├── config/                 # プロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── products/          # 商品マスタ管理
│   ├── delivery_bases/    # 配送拠点マスタ管理
│   ├── users/             # ユーザー管理
│   ├── shipment_requests/ # 出庫依頼管理
│   └── shipment_results/  # 出庫実績管理
├── static/                # 静的ファイル
├── templates/             # HTMLテンプレート
├── requirements.txt       # Pythonパッケージ
└── manage.py
```

## API仕様
詳細は`API仕様.md`を参照してください。

## データモデル
詳細は`MODEL.md`および`data_model_diagram.md`を参照してください。

## ライセンス
Proprietary
