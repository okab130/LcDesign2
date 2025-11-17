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
    
    # CORS設定
    CORS_ENABLED = os.getenv('CORS_ENABLED', 'True').lower() == 'true'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')
    
    # データベース設定
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', './mock_data.db')
