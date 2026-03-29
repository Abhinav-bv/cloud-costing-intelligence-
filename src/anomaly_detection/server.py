from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from cost_tracker import get_dashboard_stats

app = Flask(__name__)
CORS(app)

PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
CSV_PATH = os.path.join(PROJECT_ROOT, 'ml_ready_data.csv')

@app.route('/api/stats')
def stats():
    return jsonify(get_dashboard_stats(CSV_PATH))

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # For local development: use port 5000
    # For Render: use PORT environment variable (set by Render)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f'🚀 API Server online at http://localhost:{port}/api/stats')
    app.run(host='0.0.0.0', port=port, debug=debug)
