"""Server utils for CheckIt"""

from checkit.server.api import create_app

def start_app():
    """Start Flask application"""
    app = create_app()
    app.run()
