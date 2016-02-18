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
item_data = data_file['item']


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


def create_list(list_data, user_id, status=200):
    """Create a new todo list throught the API"""
    res = app.post_json('/v1/users/{user_id}/lists'.format(user_id=user_id),
                        list_data,
                        status=status,
                        expect_errors=status != 200)
    return res


def create_item(item_data, user_id, list_id, status=200):
    """Create a new item for a todo list through the API"""
    res = app.post_json('/v1/users/{user_id}/lists/{list_id}/items'.format(user_id=user_id,
                                                                           list_id=list_id),
                        item_data,
                        status=status,
                        expect_errors= status != 200)
    return res


def compare_dicts(d1, d2):
    """Checks that d1[k] == d2[k] for all keys k in d1"""
    for key in d1.keys():
        nt.assert_equals(d1[key], d2[key])


#############
# API Tests #
#############
def test_create_user():
    """Test POST for /v1/users"""
    # Create a new user with all data
    resp = create_user(user_data, status=201)
    nt.assert_equals(resp.status_code, 201)
    user = resp.json

    # Check data integrity
    compare_dicts(user_data, user)
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
    nt.assert_not_equal(resp.json['users'], [])

    user = resp.json.get('users')[0]

    # Get user with existing ID
    resp = app.get("/v1/users/{user_id}".format(user_id=user['id']))
    nt.assert_equals(resp.status_code, 200)
    nt.assert_not_equal(resp.json, {})
    user = resp.json['user']

    # Check the data
    compare_dicts(user_data, user)
    nt.assert_true(user['id'] is not None)
    user_data['id'] = user['id']

    # Get non-existing user
    resp = app.get('/v1/users/{user_id}'.format(user_id=uuid.uuid4()))
    nt.assert_equals(resp.json, {})
    nt.assert_equals(resp.status_code, 200)


def test_create_list():
    """Test POST for /v1/users/<user_id>/lists"""

    # Create correct list
    user_id = user_data['id']
    resp = create_list(list_data, user_id, status=201)
    nt.assert_equals(resp.status_code, 201)

    # Check data integrity
    list_db = resp.json
    compare_dicts(list_data, list_db)
    nt.assert_true(list_db['id'] is not None)

    # Create a list with missing data
    resp = create_list({}, user_id, status=400)
    nt.assert_equals(resp.status_code, 400)

    # Create list with wrong data
    resp = create_list({"wrong_field": "crash!"}, user_id, status=400)
    nt.assert_equals(resp.status_code, 400)

    # Save ID for firther reference
    list_data['id'] = list_db['id']


def test_get_user_lists():
    """Test GET for /v1/users/<user_id>/lists and /v1/users/<user_id>/lists/<list_id>"""

    # Get all lists (just one in this case)
    resp = app.get('/v1/users/{user_id}/lists'.format(user_id=user_data['id']))
    nt.assert_equals(resp.status_code, 200)
    nt.assert_not_equal(resp.json['lists'], [])

    # Get list with existing ID
    resp = app.get("/v1/users/{user_id}/lists/{list_id}".format(user_id=user_data['id'],
                                                                list_id=list_data['id']))
    nt.assert_equals(resp.status_code, 200)
    nt.assert_not_equal(resp.json, {})
    list_db = resp.json.get('list')

    # Check the data
    compare_dicts(list_data, list_db)
    nt.assert_true(list_db['id'] is not None)

    # Get non-existing list
    resp = app.get("/v1/users/{user_id}/lists/{list_id}".format(user_id=user_data['id'],
                                                                list_id=uuid.uuid4()))
    nt.assert_equals(resp.json, {})
    nt.assert_equals(resp.status_code, 200)


def test_create_list_item():
    """Test POST for /v1/users/<user_id>/lists/<list_id>/items"""

    # Create correct item
    user_id = user_data['id']
    list_id = list_data['id']
    resp = create_item(item_data, user_id, list_id, status=201)
    nt.assert_equals(resp.status_code, 201)

    # Check data integrity
    item_db = resp.json
    compare_dicts(item_data, item_db)
    nt.assert_true(item_db['id'] is not None)

    # Create an item with missing data
    resp = create_item({}, user_id, list_id, status=400)
    nt.assert_equals(resp.status_code, 400)

    # Create list with wrong data
    resp = create_item({"wrong_field": "crash!"}, user_id, list_id, status=400)
    nt.assert_equals(resp.status_code, 400)

    # Save ID for firther reference
    item_data['id'] = item_db['id']


def test_get_put_item():
    """Test GET and PUT for /v1/users/<user_id>/lists/<list_id>/items/<item_id>"""

    # Get all tems from a list
    resp = app.get("/v1/users/{user_id}/lists/{list_id}/items".format(user_id=user_data['id'],
                                                                      list_id=list_data['id']))
    nt.assert_equals(resp.status_code, 200)
    nt.assert_not_equal(resp.json['items'], [])

    # Get item with existing ID
    resp = app.get("/v1/users/{user_id}/lists/{list_id}/items/{item_id}".format(user_id=user_data['id'],
                                                                                list_id=list_data['id'],
                                                                                item_id=item_data['id']))
    nt.assert_equals(resp.status_code, 200)
    nt.assert_not_equal(resp.json, {})
    item_db = resp.json.get('item')

    # Check the data
    compare_dicts(item_data, item_db)
    nt.assert_true(item_db['id'] is not None)

    # Get non-existing item
    resp = app.get("/v1/users/{user_id}/lists/{list_id}/items/{item_id}".format(user_id=user_data['id'],
                                                                                list_id=list_data['id'],
                                                                                item_id=uuid.uuid4()))
    nt.assert_equals(resp.json, {})
    nt.assert_equals(resp.status_code, 200)

    # Update an existing item
    item_db['checked'] = True
    resp = app.put_json("/v1/users/{user_id}/lists/{list_id}/items/{item_id}".format(user_id=user_data['id'],
                                                                                     list_id=list_data['id'],
                                                                                     item_id=uuid.uuid4()),
                        item_db)
    nt.assert_equals(resp.status_code, 200)
    nt.assert_true(resp.json['checked'])
