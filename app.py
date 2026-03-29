"""
WSGI entry point for Render deployment
Gunicorn will use this to start the Flask application
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app from the anomaly_detection module
from src.anomaly_detection.server import app

if __name__ == '__main__':
    app.run()
