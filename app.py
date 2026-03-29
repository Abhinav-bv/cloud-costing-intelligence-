"""
WSGI entry point for Render deployment
Gunicorn will use this to start the Flask application
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'anomaly_detection'))

from server import app

if __name__ == '__main__':
    app.run()
