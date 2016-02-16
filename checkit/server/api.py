"""API endpoints"""

from flask import Flask, request, jsonify

from checkit.backend import users, todo_lists


app = Flask(__name__)

@app.route('/')
def hello_world():
    # XXX: If user authenticateed --> Load its lists, otherwise go to /login
    return 'Hello, World!'


@app.route('/v1/users', methods=['GET', 'POST'])
def get_users():
    """ Get a list of users or create a new user"""
    if request.method == 'GET':
        us = users.get_users()
        return jsonify({"users": [user.to_dict() for user in us]})
    else:
        user_data = request.json
        user = users.create_user(user_data)
        return jsonify(user.to_dict())


@app.route('/v1/users/<user_id>')
def get_user(user_id):
    """Get a specific user"""
    user = users.get_user(user_id)
    if user is not None:
        return jsonify({'user': user.to_dict()})
    else:
        return jsonify({})


@app.route('/v1/users/<user_id>/lists', methods=['GET', 'POST'])
def get_user_todo_lists(user_id):
    """Get all user's lists or create a new Todo list"""
    if request.method == 'GET':
        td_lists = todo_lists.get_todo_lists(user_id)
        return jsonify({'lists': [l.to_dict() for l in td_lists]})
    else:
        list_data = request.json
        todo_list = todo_lists.create_todo_list(list_data, user_id)
        return jsonify(todo_list.to_dict())


@app.route('/v1/users/<user_id>/lists/<list_id>')
def get_user_todo_list(user_id, list_id):
    """Get a user's concrete TODO list"""
    td_list = todo_lists.get_user_todo_list(list_id)
    return jsonify({'list': td_list.to_dict()})


@app.route('/v1/users/<user_id>/lists/<list_id>/items', methods=['GET', 'POST'])
def get_list_items(user_id, list_id):
    """Get items of a TODO list"""
    if request.method == 'GET':
        items = todo_lists.get_list_items(list_id)
        return jsonify({"items": [item.to_dict() for item in items]})
    else:
        item_data = request.json
        item = todo_lists.create_item(list_id, item_data)
        return jsonify(item.to_dict())


@app.route('/v1/users/<user_id>/lists/<list_id>/items/<item_id>', methods=['PUT'])
def update_item(user_id, list_id, item_id):
    """Modify an existing item"""
    new_item_data = request.json
    mod_item = todo_lists.update_item(item_data)
    return jsonify(mod_item.to_dict())
