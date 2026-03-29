from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from cost_tracker import get_dashboard_stats, log_intervention
from flask import request as flask_request

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


@app.route('/api/log_intervention', methods=['POST'])
def log_intervention_api():
    data = None
    try:
        data = flask_request.get_json()
    except Exception:
        data = None

    if not data:
        return jsonify({"error": "invalid payload"}), 400

    resource_id = data.get('resource_id')
    action_type = data.get('action_type', 'autonomously_stopped')
    anomaly_score = data.get('anomaly_score', 0.0)
    savings_usd = data.get('savings_usd', 0.0)

    entry = log_intervention(resource_id, action_type, anomaly_score, savings_usd)
    return jsonify(entry), 201

if __name__ == '__main__':
    # For local development: use port 5000
    # For Render: use PORT environment variable (set by Render)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f'🚀 API Server online at http://localhost:{port}/api/stats')
    app.run(host='0.0.0.0', port=port, debug=debug)
