"""API endpoints"""

from flask import Flask, jsonify

from checkit.backend import users


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/v1/users')
def get_users():
    us = users.get_users()
    return jsonify({"users": [user.to_dict() for user in us]})
