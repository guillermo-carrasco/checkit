"""Server utils for CheckIt"""

from checkit.server import api

def start_app():
    """Start Flask application"""
    app = api.get_app()
    app.run()
