"""API endpoints"""

from flask import Flask, request, jsonify

from checkit.backend import users, todo_lists


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/v1/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        us = users.get_users()
        return jsonify({"users": [user.to_dict() for user in us]})
    else:
        user_data = request.json
        user = users.create_user(user_data)
        return jsonify(user.to_dict())

@app.route('/v1/users/<user_id>')
def get_user(user_id):
    user = users.get_user(user_id)
    if user is not None:
        return jsonify({'user': user.to_dict()})
    else:
        return jsonify({})

@app.route('/v1/users/<user_id>/lists')
def get_user_todo_lists(user_id):
    td_lists = todo_lists.get_todo_lists(user_id)
    if td_lists is not None:
        return jsonify({'lists': [l.to_dict() for l in td_lists]})
    else:
        return jsonify({})
