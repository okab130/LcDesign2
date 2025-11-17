import sqlite3
import json
from datetime import datetime
from config import Config


class Database:
    """SQLiteデータベース管理クラス"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.SQLITE_DB_PATH
        self.init_db()
    
    def get_connection(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """データベース初期化"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 在庫テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventories (
                pallet_id TEXT PRIMARY KEY,
                product_code TEXT NOT NULL,
                location_code TEXT NOT NULL,
                factory_code TEXT NOT NULL,
                line_code TEXT NOT NULL,
                production_number TEXT NOT NULL,
                production_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_type TEXT NOT NULL,
                entry_datetime TEXT NOT NULL
            )
        ''')
        
        # 出庫依頼テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shipment_requests (
                request_id TEXT PRIMARY KEY,
                base_code TEXT NOT NULL,
                delivery_date TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # エラーモードテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_modes (
                endpoint TEXT PRIMARY KEY,
                error_type TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # デフォルトデータがない場合は挿入
        self.init_default_data()
    
    def init_default_data(self):
        """デフォルトテストデータの初期化"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 既存データがあるかチェック
        cursor.execute('SELECT COUNT(*) as count FROM inventories')
        count = cursor.fetchone()['count']
        
        if count == 0:
            # デフォルト在庫データ
            default_inventories = [
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
                },
                {
                    "pallet_id": "PLT-20231115-003",
                    "product_code": "PRD001",
                    "location_code": "A-02-01",
                    "factory_code": "F001",
                    "line_code": "L001",
                    "production_number": "20231115-003",
                    "production_date": "2023-11-15",
                    "expiry_date": "2024-11-15",
                    "quantity": 200,
                    "entry_type": "AUTO",
                    "entry_datetime": "2023-11-15T10:00:00Z"
                },
                {
                    "pallet_id": "PLT-20231115-004",
                    "product_code": "PRD003",
                    "location_code": "A-02-02",
                    "factory_code": "F002",
                    "line_code": "L003",
                    "production_number": "20231115-004",
                    "production_date": "2023-11-15",
                    "expiry_date": "2024-11-15",
                    "quantity": 120,
                    "entry_type": "AUTO",
                    "entry_datetime": "2023-11-15T11:00:00Z"
                },
                {
                    "pallet_id": "PLT-20231115-005",
                    "product_code": "PRD002",
                    "location_code": "A-03-01",
                    "factory_code": "F001",
                    "line_code": "L002",
                    "production_number": "20231115-005",
                    "production_date": "2023-11-15",
                    "expiry_date": "2024-11-15",
                    "quantity": 180,
                    "entry_type": "AUTO",
                    "entry_datetime": "2023-11-15T12:00:00Z"
                }
            ]
            
            for inv in default_inventories:
                cursor.execute('''
                    INSERT INTO inventories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    inv['pallet_id'],
                    inv['product_code'],
                    inv['location_code'],
                    inv['factory_code'],
                    inv['line_code'],
                    inv['production_number'],
                    inv['production_date'],
                    inv['expiry_date'],
                    inv['quantity'],
                    inv['entry_type'],
                    inv['entry_datetime']
                ))
            
            conn.commit()
        
        conn.close()
    
    def get_all_inventories(self):
        """全在庫データを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventories')
        rows = cursor.fetchall()
        conn.close()
        
        inventories = []
        for row in rows:
            inventories.append(dict(row))
        
        return inventories
    
    def add_inventory(self, inventory):
        """在庫データを追加"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO inventories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inventory['pallet_id'],
            inventory['product_code'],
            inventory['location_code'],
            inventory['factory_code'],
            inventory['line_code'],
            inventory['production_number'],
            inventory['production_date'],
            inventory['expiry_date'],
            inventory['quantity'],
            inventory['entry_type'],
            inventory['entry_datetime']
        ))
        
        conn.commit()
        conn.close()
    
    def clear_inventories(self):
        """全在庫データをクリア"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventories')
        conn.commit()
        conn.close()
    
    def reset_inventories(self):
        """在庫データをデフォルトにリセット"""
        self.clear_inventories()
        self.init_default_data()
    
    def add_shipment_request(self, request_id, base_code, delivery_date, details):
        """出庫依頼を保存"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shipment_requests VALUES (?, ?, ?, ?, ?)
        ''', (
            request_id,
            base_code,
            delivery_date,
            json.dumps(details),
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_shipment_request(self, request_id):
        """出庫依頼を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM shipment_requests WHERE request_id = ?', (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def set_error_mode(self, endpoint, error_type):
        """エラーモードを設定"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO error_modes VALUES (?, ?, 1)
        ''', (endpoint, error_type))
        
        conn.commit()
        conn.close()
    
    def get_error_mode(self, endpoint):
        """エラーモードを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM error_modes WHERE endpoint = ? AND enabled = 1', (endpoint,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def clear_error_modes(self):
        """全エラーモードをクリア"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM error_modes')
        conn.commit()
        conn.close()
