"""Server utils for CheckIt"""
import os

from checkit.backend import setup_stores
from checkit.server.api import app

def start_app():
    """Start and configure Flask application"""
    DB_URI = os.environ.get('DB_URI', 'sqlite:////tmp/checkit_db.db')
    setup_stores(DB_URI)

    app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
    app.config['GITHUB_CLIENT'] = os.environ.get('GITHUB_CLIENT')

    app.run(debug=True)
    return app
