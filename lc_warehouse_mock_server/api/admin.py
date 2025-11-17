import requests
from flask import Blueprint, request, jsonify
from database import Database

admin_bp = Blueprint('admin', __name__)
db = Database()


@admin_bp.route('/api/v1/admin/inventory', methods=['POST'])
def add_inventory():
    """在庫データ追加API"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Request body is required'
        }), 400
    
    # 必須項目チェック
    required_fields = ['pallet_id', 'product_code', 'location_code', 'factory_code', 
                      'line_code', 'production_number', 'production_date', 'expiry_date',
                      'quantity', 'entry_type', 'entry_datetime']
    
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 'error',
                'message': f'{field} is required'
            }), 400
    
    try:
        db.add_inventory(data)
        return jsonify({
            'status': 'success',
            'message': 'Inventory added'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_bp.route('/api/v1/admin/inventory', methods=['DELETE'])
def clear_inventory():
    """在庫データクリアAPI"""
    try:
        db.clear_inventories()
        return jsonify({
            'status': 'success',
            'message': 'All inventory data cleared'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_bp.route('/api/v1/admin/inventory/reset', methods=['POST'])
def reset_inventory():
    """在庫データ初期化API"""
    try:
        db.reset_inventories()
        inventories = db.get_all_inventories()
        return jsonify({
            'status': 'success',
            'message': 'Inventory data reset to default',
            'count': len(inventories)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_bp.route('/api/v1/admin/error-mode', methods=['POST'])
def set_error_mode():
    """エラーモード設定API"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Request body is required'
        }), 400
    
    endpoint = data.get('endpoint')
    error_type = data.get('error_type')
    
    if not endpoint or not error_type:
        return jsonify({
            'status': 'error',
            'message': 'endpoint and error_type are required'
        }), 400
    
    try:
        db.set_error_mode(endpoint, error_type)
        return jsonify({
            'status': 'success',
            'message': f'Error mode set for {endpoint}'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_bp.route('/api/v1/admin/error-mode', methods=['DELETE'])
def clear_error_mode():
    """エラーモードクリアAPI"""
    try:
        db.clear_error_modes()
        return jsonify({
            'status': 'success',
            'message': 'All error modes cleared'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_bp.route('/api/v1/admin/send-webhook', methods=['POST'])
def send_webhook():
    """手動Webhook送信API（認証なし）"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Request body is required'
        }), 400
    
    target_url = data.get('target_url')
    results = data.get('results', [])
    
    if not target_url:
        return jsonify({
            'status': 'error',
            'message': 'target_url is required'
        }), 400
    
    if not results:
        return jsonify({
            'status': 'error',
            'message': 'results is required'
        }), 400
    
    # Webhookリクエストを送信（認証なし）
    try:
        response = requests.post(
            target_url,
            json={'results': results},
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook sent successfully',
            'response_status': response.status_code,
            'response_body': response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
        }), 200
        
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Webhook request timeout'
        }), 500
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Webhook request failed: {str(e)}'
        }), 500
