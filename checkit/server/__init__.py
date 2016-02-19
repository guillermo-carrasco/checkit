"""Server utils for CheckIt"""
import os

from checkit.backend import setup_stores
from checkit.server.api import app


"""Start and configure Flask application"""
DB_URI = os.environ.get('DB_URI')
setup_stores(DB_URI)

app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
app.config['GITHUB_CLIENT'] = os.environ.get('GITHUB_CLIENT')

def start_app():
    app.run(debug=True)
