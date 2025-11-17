import time
from flask import Blueprint, request, jsonify
from auth.jwt_manager import require_jwt_auth
from database import Database

shipment_requests_bp = Blueprint('shipment_requests', __name__)
db = Database()


@shipment_requests_bp.route('/api/v1/shipment-requests', methods=['POST'])
@require_jwt_auth
def create_shipment_requests():
    """出庫依頼送信API"""
    
    # エラーモードチェック
    error_mode = db.get_error_mode('/api/v1/shipment-requests')
    
    if error_mode:
        error_type = error_mode['error_type']
        
        if error_type == 'timeout':
            time.sleep(65)
            return jsonify({
                'error': 'timeout',
                'error_description': 'Request timeout'
            }), 504
        
        elif error_type == 'auth_error':
            return jsonify({
                'error': 'unauthorized',
                'error_description': 'Invalid or expired JWT token'
            }), 401
        
        elif error_type == 'server_error':
            return jsonify({
                'error': 'internal_server_error',
                'error_description': 'An unexpected error occurred'
            }), 500
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'Request body is required'
        }), 400
    
    requests_list = data.get('requests', [])
    
    if not requests_list:
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'requests is required'
        }), 400
    
    # バリデーション
    errors = validate_shipment_requests(requests_list)
    if errors:
        return jsonify({
            'error': 'validation_error',
            'error_description': 'Invalid request data',
            'errors': errors
        }), 400
    
    # 出庫依頼を処理
    results = []
    
    for req in requests_list:
        request_id = req['request_id']
        base_code = req['base_code']
        delivery_date = req['delivery_date']
        details = req['details']
        
        # 在庫不足チェック（シミュレーション）
        insufficient_inventory_mode = db.get_error_mode('/api/v1/shipment-requests/insufficient_inventory')
        
        if insufficient_inventory_mode:
            # 在庫不足エラーシミュレーション
            results.append({
                'request_id': request_id,
                'status': 'error',
                'error_code': 'insufficient_inventory',
                'message': f'Insufficient inventory for product {details[0]["product_code"]}'
            })
        else:
            # 出庫依頼を保存
            db.add_shipment_request(request_id, base_code, delivery_date, details)
            
            results.append({
                'request_id': request_id,
                'status': 'success',
                'message': 'Request accepted'
            })
    
    return jsonify({
        'results': results
    }), 200


def validate_shipment_requests(requests_list):
    """出庫依頼のバリデーション"""
    errors = []
    
    for i, req in enumerate(requests_list):
        # 必須項目チェック
        if 'request_id' not in req:
            errors.append({
                'field': f'requests[{i}].request_id',
                'message': 'request_id is required'
            })
        
        if 'base_code' not in req:
            errors.append({
                'field': f'requests[{i}].base_code',
                'message': 'base_code is required'
            })
        
        if 'delivery_date' not in req:
            errors.append({
                'field': f'requests[{i}].delivery_date',
                'message': 'delivery_date is required'
            })
        
        if 'details' not in req or not isinstance(req['details'], list) or len(req['details']) == 0:
            errors.append({
                'field': f'requests[{i}].details',
                'message': 'details must be a non-empty array'
            })
        else:
            # 明細のバリデーション
            for j, detail in enumerate(req['details']):
                if 'line_number' not in detail:
                    errors.append({
                        'field': f'requests[{i}].details[{j}].line_number',
                        'message': 'line_number is required'
                    })
                
                if 'product_code' not in detail:
                    errors.append({
                        'field': f'requests[{i}].details[{j}].product_code',
                        'message': 'product_code is required'
                    })
                
                if 'quantity' not in detail:
                    errors.append({
                        'field': f'requests[{i}].details[{j}].quantity',
                        'message': 'quantity is required'
                    })
                elif not isinstance(detail['quantity'], int) or detail['quantity'] <= 0:
                    errors.append({
                        'field': f'requests[{i}].details[{j}].quantity',
                        'message': 'Quantity must be a positive integer'
                    })
    
    return errors
