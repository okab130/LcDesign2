from flask import Blueprint, request, jsonify
from auth.jwt_manager import JWTManager
from config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/v1/auth/token', methods=['POST'])
def get_token():
    """JWT認証トークン取得API"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'Request body is required'
        }), 400
    
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not client_id or not client_secret:
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'client_id and client_secret are required'
        }), 400
    
    # クライアント認証
    if not JWTManager.authenticate_client(client_id, client_secret):
        return jsonify({
            'error': 'invalid_client',
            'error_description': 'Invalid client credentials'
        }), 401
    
    # トークン生成
    access_token = JWTManager.generate_access_token(client_id)
    refresh_token = JWTManager.generate_refresh_token(client_id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES,
        'refresh_expires_in': Config.JWT_REFRESH_TOKEN_EXPIRES
    }), 200


@auth_bp.route('/api/v1/auth/refresh', methods=['POST'])
def refresh_token():
    """トークンリフレッシュAPI"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'Request body is required'
        }), 400
    
    refresh_token_str = data.get('refresh_token')
    
    if not refresh_token_str:
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'refresh_token is required'
        }), 400
    
    # リフレッシュトークンを検証
    payload = JWTManager.verify_token(refresh_token_str, token_type='refresh')
    
    if not payload:
        return jsonify({
            'error': 'invalid_token',
            'error_description': 'Refresh token is expired or invalid'
        }), 401
    
    # 新しいアクセストークンを生成
    client_id = payload.get('client_id')
    access_token = JWTManager.generate_access_token(client_id)
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': Config.JWT_ACCESS_TOKEN_EXPIRES
    }), 200
