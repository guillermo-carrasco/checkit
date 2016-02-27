"""API endpoints"""
import os

from flask import (Flask, g, session, redirect, flash, abort, request, url_for,
                   jsonify, make_response)
from flask.ext.github import GitHub
from sqlalchemy.exc import OperationalError

from checkit.backend import users, todo_lists, setup_stores
from checkit.utils import config


app = Flask(__name__, static_url_path='/static')
app.config.update(config.get_github_confs())
app.secret_key = config.get_app_secret()

github = GitHub(app)

class InvalidAPIUsage(Exception):
    """Handle invalid API calls"""
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


@app.route('/v1/users/<user_id>/lists/<list_id>', methods=['GET', 'DELETE'])
def get_user_todo_list(user_id, list_id):
    """Get a user's concrete TODO list"""
    if request.method == 'GET':
        td_list = todo_lists.get_user_todo_list(list_id)
        if td_list is not None:
            return jsonify({'list': td_list.to_dict()})
        else:
            return jsonify({})
    else:
        removed = todo_lists.delete_todo_list(list_id)
        if removed:
            return make_response(jsonify({}), 200)
        else:
            return make_response(jsonify({'message': 'Could not remove the list'}), 400)



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
    DB_URI = os.environ.get('DB_URI')
    setup_stores(DB_URI)
    users.reset()
    users.bootstrap()
    todo_lists.reset()
    todo_lists.bootstrap()
    return app.send_static_file('index.html')


#################
# Authorization #
#################
@app.before_request
def before_request():
    """Check if user is loged in and with a valid token on every request"""
    g.user = None
    if 'user_token' in session:
        try:
            g.user = users.get_user_by_token(session['user_token'])
        except OperationalError:
            return None


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.gh_token
    return None



@app.route('/')
def index():
    if g.user:
        if g.user.email is None:
            user_data = github.get('user')
            g.user.email = user_data['email']
            g.user.name = user_data['name']
            users.update_user(g.user.to_dict())
        return app.send_static_file('app.html')

    return app.send_static_file('index.html')


@app.route('/login')
def login():
    return github.authorize()


@app.route('/logout')
def logout():
    session.pop('user_token', None)
    return redirect(url_for('index'))


@app.route('/authorized')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization with GitHub failed.")
        return redirect(next_url)

    user_obj = users.get_user_by_token(oauth_token)
    if user_obj is None:
        user_obj = users.create_user({'gh_token': oauth_token})

    session['user_token'] = user_obj.gh_token
    return redirect(next_url)


@app.route('/user')
def user():
    if g.user:
        return jsonify(**g.user.to_dict())
    else:
        return abort(500)
