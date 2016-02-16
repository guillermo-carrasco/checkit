"""API endpoints"""

from flask import Flask, request, jsonify

from checkit.backend import users


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/v1/users/<user_id>')
def get_user(user_id):
    user = users.get_user(user_id)
    if user is not None:
        return jsonify({'user': user})
    else:
        return jsonify({})

@app.route('/v1/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        us = users.get_users()
        return jsonify({"users": [user.to_dict() for user in us]})
    else:
        user_data = request.json
        user = users.create_user(user_data)
        return jsonify(user.to_dict())
