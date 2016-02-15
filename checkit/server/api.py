"""API endpoints"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# Use SQLite by default if no other DB is specifyed
DB_URI = os.environ.get('DB_URI', 'sqlite:////tmp/checkit_db.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(app)
db.create_all()

def get_app():
    """Return app object for outside use"""
    return app


def get_db():
    """Return SQLAlchemy object for outside use"""
    return db

@app.route('/')
def hello_world():
    return 'Hello, World!'


def get_app():
    """Return app object for outside use"""
    return app


def get_db():
    """Return SQLAlchemy object for outside use"""
    return db
