"""API endpoints"""
import os
import json

import requests
import jwt

from datetime import datetime, timedelta
from urlparse import parse_qsl

from flask import Flask, request, jsonify, make_response, render_template

from checkit.backend import users, todo_lists, setup_stores


app = Flask(__name__, static_url_path='/static')

class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def landing_page():
    return app.send_static_file('index.html')


@app.route('/v1/users', methods=['GET', 'POST'])
def get_users():
    """ Get a list of users or create a new user"""
    if request.method == 'GET':
        us = users.get_users()
        return jsonify({"users": [user.to_dict() for user in us]})
    else:
        user_data = request.json
        try:
            user = users.create_user(user_data)
        except:
            raise InvalidAPIUsage('Wrong or incomplete user data', status_code=400)
        return make_response(jsonify(user.to_dict()), 201)


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
        try:
            todo_list = todo_lists.create_todo_list(list_data, user_id)
        except:
            raise InvalidAPIUsage("Wrong or incomplete todo_list data")
        return make_response(jsonify(todo_list.to_dict()), 201)


@app.route('/v1/users/<user_id>/lists/<list_id>')
def get_user_todo_list(user_id, list_id):
    """Get a user's concrete TODO list"""
    td_list = todo_lists.get_user_todo_list(list_id)
    if td_list is not None:
        return jsonify({'list': td_list.to_dict()})
    else:
        return jsonify({})


@app.route('/v1/users/<user_id>/lists/<list_id>/items', methods=['GET', 'POST'])
def get_list_items(user_id, list_id):
    """Get items of a TODO list"""
    if request.method == 'GET':
        items = todo_lists.get_list_items(list_id)
        return jsonify({"items": [item.to_dict() for item in items]})
    else:
        item_data = request.json
        try:
            item = todo_lists.create_item(list_id, item_data)
        except:
            raise InvalidAPIUsage("Wrong or incomplete item data")
        return make_response(jsonify(item.to_dict()), 201)


@app.route('/v1/users/<user_id>/lists/<list_id>/items/<item_id>')
def get_item(user_id, list_id, item_id):
    """Get a TODO list's concrete item"""
    item_list = todo_lists.get_item(item_id)
    if item_list is not None:
        return jsonify({'item': item_list.to_dict()})
    else:
        return jsonify({})


@app.route('/v1/users/<user_id>/lists/<list_id>/items/<item_id>', methods=['PUT'])
def update_item(user_id, list_id, item_id):
    """Modify an existing item"""
    item_data = request.json
    mod_item = todo_lists.update_item(item_data)
    if mod_item is not None:
        return jsonify(mod_item.to_dict())
    else:
        return jsonify({})


@app.route('/v1/1000fc1e-56dc-4a7d-add0-a83d1120c5d7')
def _reset_db():
    """_secret_ endpoint to cleanup and setup the database"""
    DB_URI = os.environ.get('DB_URI', 'sqlite:////tmp/checkit_db.db')
    setup_stores(DB_URI)
    users.reset()
    users.bootstrap()
    todo_lists.reset()
    todo_lists.bootstrap()
    return app.send_static_file('index.html')


#################
# Authorization #
#################
def create_token(user):
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    token = jwt.encode(payload, app.config['GITHUB_SECRET'])
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['GITHUB_SECRET'])


@app.route('/auth/github', methods=['POST'])
def github():
    access_token_url = 'https://github.com/login/oauth/access_token'
    users_api_url = 'https://api.github.com/user'

    params = {
        'client_id': request.json['clientId'],
        'redirect_uri': request.json['redirectUri'],
        'client_secret': app.config['GITHUB_SECRET'],
        'code': request.json['code']
    }

    # Step 1. Exchange authorization code for access token.
    r = requests.get(access_token_url, params=params)
    access_token = dict(parse_qsl(r.text))
    headers = {'User-Agent': 'Satellizer'}

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params=access_token, headers=headers)
    profile = json.loads(r.text)

    # Step 3. Create a new account or return an existing one.
    user = users.get_user(profile['id'])
    if user:
        token = create_token(user)
        return jsonify(token=token)
    else:
        user = users.create_user({'id': profile['id'], 'name': profile['name']})
        token = create_token(user)
        return jsonify(token=token)
