import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class Config:
    """モックサーバ設定"""
    
    # サーバ設定
    HOST = os.getenv('MOCK_SERVER_HOST', '0.0.0.0')
    PORT = int(os.getenv('MOCK_SERVER_PORT', 5001))
    DEBUG = os.getenv('MOCK_SERVER_DEBUG', 'True').lower() == 'true'
    
    # JWT設定
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mock_jwt_secret_key_do_not_use_in_production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1800))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 86400))
    
    # CORS設定
    CORS_ENABLED = os.getenv('CORS_ENABLED', 'True').lower() == 'true'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')
    
    # データベース設定
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', './mock_data.db')
    
    # デフォルトクライアント認証情報
    DEFAULT_CLIENT_ID = 'shipment_system_client'
    DEFAULT_CLIENT_SECRET = 'mock_secret_key_12345'
