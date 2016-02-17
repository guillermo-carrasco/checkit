import codecs
import copy
import json
import os
import uuid

import nose.tools as nt

from webtest import TestApp

import checkit.server.api as api
from checkit.backend import setup_stores, users, todo_lists

########################
# Tests initialization #
########################

# Create and initialize the test database and the application
DB_URI = os.environ.get('TEST_DB_URI', 'sqlite:////tmp/checkit_db.db')
setup_stores(DB_URI)
users.bootstrap()
users.reset()
todo_lists.bootstrap()
todo_lists.reset()

app = TestApp(api.app)


# Load test data
data_file = codecs.open("./tests/test_data.json", "r", "utf-8").read()
data_file = json.loads(data_file)
user_data = data_file['user']
list_data = data_file['list']
list_items = data_file['items']


########################
# Convinience  methods #
########################
def create_user(user_data, status=200):
    """Create a new user throught the API"""
    user_data = user_data
    res = app.post_json('/v1/users',
                        user_data,
                        status=status,
                        expect_errors=status != 200)
    return res

def create_list(list_data, status=200):
    """Create a new todo list throught the API"""
    list_data = list_data
    res = app.post_json('/v1/users/{user_id}/lists'.format(user_id=list_data['user_id']),
                        list_data,
                        status=status,
                        expect_errors=status != 200)
    return res


#############
# API Tests #
#############
def test_create_user():
    """Test POST for /v1/users"""
    # Create a new user with all data
    user = create_user(user_data).json

    for key in user_data.keys():
        nt.assert_equals(user[key], user_data[key])
    nt.assert_true(user['id'] is not None)

    # Create a user with missing data
    resp = create_user({}, status=400)
    nt.assert_equals(resp.status_code, 400)

    # Create user with wrong data
    resp = create_user({"wrong_field": "crash!"}, status=400)
    nt.assert_equals(resp.status_code, 400)


def test_get_users():
    """Test GET for /v1/users and /v1/users/<user_id>"""

    resp = app.get('/v1/users')
    nt.assert_equals(resp.status_code, 200)
    nt.assert_is_not_none(resp.json)

    user = resp.json.get('users')[0]

    # Get user with existing ID
    resp = app.get("/v1/users/{user_id}".format(user_id=user['id']))
    nt.assert_equals(resp.status_code, 200)

    # Check the data
    for key in user_data.keys():
        nt.assert_equals(user[key], user_data[key])
    nt.assert_true(user['id'] is not None)

    # Get non-existing user
    resp = app.get('/v1/users/{user_id}'.format(user_id=uuid.uuid4()))
    nt.assert_equals(resp.json, {})
    nt.assert_equals(resp.status_code, 200)


def test_get_user_lists():
    """Test GET for /v1/users/<user_id>/lists"""

    # Get existing user in the database to be referenced by ID
    user = app.get("/v1/users").json.get('users')[0]
    user_id = user['id']
    resp = app.get('/v1/users/{user_id}/lists'.format(user_id=user_id))
    nt.assert_equals(resp.status_code, 200)
