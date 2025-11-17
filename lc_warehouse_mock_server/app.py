from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from api.inventory import inventory_bp
from api.shipment_requests import shipment_requests_bp
from api.admin import admin_bp
import logging

# Flaskアプリケーション作成
app = Flask(__name__)

# CORS設定
if Config.CORS_ENABLED:
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# ログ設定
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

# Blueprintを登録
app.register_blueprint(inventory_bp)
app.register_blueprint(shipment_requests_bp)
app.register_blueprint(admin_bp)


@app.route('/', methods=['GET'])
def index():
    """ルートエンドポイント"""
    return jsonify({
        'name': 'LC Warehouse Mock Server',
        'version': '1.0',
        'status': 'running',
        'note': 'Development/Test environment - No authentication required'
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    return jsonify({
        'error': 'not_found',
        'error_description': 'The requested endpoint was not found'
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    """500エラーハンドラー"""
    return jsonify({
        'error': 'internal_server_error',
        'error_description': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    print(f"Starting LC Warehouse Mock Server on {Config.HOST}:{Config.PORT}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"CORS enabled: {Config.CORS_ENABLED}")
    print("NOTE: Running in development mode - No authentication required")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
