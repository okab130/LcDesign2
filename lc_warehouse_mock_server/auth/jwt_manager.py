import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config


class JWTManager:
    """JWT認証管理クラス"""
    
    @staticmethod
    def generate_access_token(client_id):
        """アクセストークンを生成"""
        payload = {
            'client_id': client_id,
            'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def generate_refresh_token(client_id):
        """リフレッシュトークンを生成"""
        payload = {
            'client_id': client_id,
            'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """トークンを検証"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            
            if payload.get('type') != token_type:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def authenticate_client(client_id, client_secret):
        """クライアント認証"""
        if client_id == Config.DEFAULT_CLIENT_ID and client_secret == Config.DEFAULT_CLIENT_SECRET:
            return True
        return False


def require_jwt_auth(f):
    """JWT認証デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'unauthorized',
                'error_description': 'Missing Authorization header'
            }), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'error': 'unauthorized',
                'error_description': 'Invalid Authorization header format'
            }), 401
        
        payload = JWTManager.verify_token(token, token_type='access')
        
        if not payload:
            return jsonify({
                'error': 'unauthorized',
                'error_description': 'Invalid or expired JWT token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
