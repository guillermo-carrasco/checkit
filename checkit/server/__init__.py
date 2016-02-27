"""Server utils for CheckIt"""
from checkit.backend import setup_stores
from checkit.server.api import app
from checkit.utils import config


"""Start and configure Flask application"""
DB_URI = config.get_db_url()
setup_stores(DB_URI)

def start_app():
    app.run(debug=True)
