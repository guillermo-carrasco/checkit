"""API endpoints"""
from flask import Flask

def create_app():
    """Create a Flask app with al API endpoints"""

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    return app
