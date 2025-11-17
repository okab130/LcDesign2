import time
from flask import Blueprint, jsonify
from auth.jwt_manager import require_jwt_auth
from database import Database

inventory_bp = Blueprint('inventory', __name__)
db = Database()


@inventory_bp.route('/api/v1/inventory', methods=['GET'])
@require_jwt_auth
def get_inventory():
    """在庫情報取得API"""
    
    # エラーモードチェック
    error_mode = db.get_error_mode('/api/v1/inventory')
    
    if error_mode:
        error_type = error_mode['error_type']
        
        if error_type == 'timeout':
            # タイムアウトシミュレーション（35秒待機）
            time.sleep(35)
            return jsonify({
                'error': 'timeout',
                'error_description': 'Request timeout'
            }), 504
        
        elif error_type == 'auth_error':
            # 認証エラーシミュレーション
            return jsonify({
                'error': 'unauthorized',
                'error_description': 'Invalid or expired JWT token'
            }), 401
        
        elif error_type == 'server_error':
            # サーバーエラーシミュレーション
            return jsonify({
                'error': 'internal_server_error',
                'error_description': 'An unexpected error occurred'
            }), 500
    
    # 在庫データ取得
    inventories = db.get_all_inventories()
    
    return jsonify({
        'inventories': inventories,
        'total_count': len(inventories)
    }), 200
