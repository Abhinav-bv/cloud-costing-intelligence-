from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from cost_tracker import get_dashboard_stats

app = Flask(__name__)
CORS(app)  # Vital for React connectivity

# ✅ Point directly to the CSV in the project root
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
CSV_PATH = os.path.join(PROJECT_ROOT, 'ml_ready_data.csv')

@app.route('/api/stats')
def stats():
    return jsonify(get_dashboard_stats(CSV_PATH))

if __name__ == '__main__':
    print("🚀 API Server online at http://localhost:5000/api/stats")
    app.run(port=5000, debug=True)