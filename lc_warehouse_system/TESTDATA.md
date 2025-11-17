# テストデータ投入スクリプト

## 使用方法

```bash
python manage.py shell < scripts/load_test_data.py
```

または、Djangoシェルで直接実行：

```bash
python manage.py shell
```

```python
from apps.products.models import Product
from apps.delivery_bases.models import DeliveryBase
from apps.users.models import User

# 商品マスタ
products = [
    {"product_code": "P001", "product_name": "アルコーラ", "pallet_case_quantity": 100},
    {"product_code": "P002", "product_name": "アルコーヒー", "pallet_case_quantity": 120},
    {"product_code": "P003", "product_name": "アルオレンジ", "pallet_case_quantity": 80},
    {"product_code": "P004", "product_name": "アルミルク", "pallet_case_quantity": 150},
]

for p in products:
    Product.objects.get_or_create(**p)

print("商品マスタ登録完了")

# 配送拠点マスタ
bases = [
    {"base_code": "B001", "base_name": "東京配送センター"},
    {"base_code": "B002", "base_name": "大阪配送センター"},
    {"base_code": "B003", "base_name": "名古屋配送センター"},
    {"base_code": "B004", "base_name": "福岡配送センター"},
    {"base_code": "B005", "base_name": "札幌配送センター"},
]

for b in bases:
    DeliveryBase.objects.get_or_create(**b)

print("配送拠点マスタ登録完了")

# ユーザー
# 管理者
admin_user, created = User.objects.get_or_create(
    user_id="admin",
    defaults={
        "user_name": "システム管理者",
        "user_type": "ADMIN",
        "is_staff": True,
        "is_superuser": True,
    }
)
if created:
    admin_user.set_password("admin123")
    admin_user.save()

# LC倉庫担当
lc_staff, created = User.objects.get_or_create(
    user_id="lc_staff001",
    defaults={
        "user_name": "LC倉庫担当者1",
        "user_type": "LC_STAFF",
    }
)
if created:
    lc_staff.set_password("lc123")
    lc_staff.save()

# 拠点倉庫担当
tokyo_base = DeliveryBase.objects.get(base_code="B001")
base_staff, created = User.objects.get_or_create(
    user_id="base_staff001",
    defaults={
        "user_name": "東京拠点担当者1",
        "user_type": "BASE_STAFF",
        "base_code": tokyo_base,
    }
)
if created:
    base_staff.set_password("base123")
    base_staff.save()

print("ユーザー登録完了")
print("\n=== テストデータ投入完了 ===")
print("\nログイン情報:")
print("管理者: admin / admin123")
print("LC倉庫担当: lc_staff001 / lc123")
print("拠点倉庫担当: base_staff001 / base123")
```
