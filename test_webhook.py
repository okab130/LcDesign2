"""
出庫実績Webhook送信テスト
"""
import requests
import json
from datetime import datetime, timedelta

# テスト用の出庫実績データ
test_results = {
    "results": [
        {
            "result_id": "RES-20251117-001",
            "request_id": "SR20251117-0001",  # 実際に登録した出庫依頼ID
            "pallet_id": "PLT-20251117-001",
            "product_code": "PROD001",  # 実際に登録した商品コード
            "quantity": 10,
            "shipment_type": "AUTO",
            "shipment_datetime": datetime.now().isoformat(),
            "base_code": "BASE001",  # 実際に登録した配送拠点コード
            "location_code": "A-01-01",
            "factory_code": "F001",
            "line_code": "L001",
            "production_number": "20251117-001",
            "production_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "expiry_date": (datetime.now() + timedelta(days=330)).strftime("%Y-%m-%d")
        },
        {
            "result_id": "RES-20251117-002",
            "request_id": "SR20251117-0001",
            "pallet_id": "PLT-20251117-002",
            "product_code": "PROD002",
            "quantity": 5,
            "shipment_type": "AUTO",
            "shipment_datetime": datetime.now().isoformat(),
            "base_code": "BASE001",
            "location_code": "A-01-02",
            "factory_code": "F001",
            "line_code": "L002",
            "production_number": "20251117-002",
            "production_date": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
            "expiry_date": (datetime.now() + timedelta(days=335)).strftime("%Y-%m-%d")
        }
    ]
}

# 本システムのWebhookエンドポイント
webhook_url = "http://localhost:8000/api/v1/shipment-results/webhook/"

print("=" * 60)
print("出庫実績Webhook送信テスト")
print("=" * 60)
print(f"送信先: {webhook_url}")
print(f"送信データ:")
print(json.dumps(test_results, indent=2, ensure_ascii=False))
print("=" * 60)

try:
    response = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        json=test_results,
        timeout=10
    )
    
    print(f"\n✅ ステータスコード: {response.status_code}")
    print(f"✅ レスポンス:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 201:
        print("\n🎉 出庫実績の送信に成功しました！")
        print(f"📋 画面で確認: http://localhost:8000/shipment-result/")
    else:
        print("\n⚠️ エラーが発生しました")
        
except requests.exceptions.ConnectionError:
    print("\n❌ エラー: 本システムに接続できません")
    print("開発サーバーが起動していることを確認してください:")
    print("  cd C:\\Users\\user\\gh\\LcDesign2\\lc_warehouse_system")
    print("  python manage.py runserver 8000")
    
except Exception as e:
    print(f"\n❌ エラー: {str(e)}")
