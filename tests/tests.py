import codecs
import copy
import json
import os
import uuid

import nose.tools as nt

from webtest import TestApp

import checkit.server.api as api
from checkit.backend import setup_stores, users, todo_lists

app = None

def setup(module):
    """Create and initialize the test database and the application"""
    DB_URI = os.environ.get('TEST_DB_URI', 'sqlite:////tmp/checkit_db.db')
    setup_stores(DB_URI)
    users.bootstrap()
    users.reset()
    todo_lists.bootstrap()
    todo_lists.reset()

    app = api.app
    module.app = TestApp(app)


class TestDataLoader(object):
    """Simple abstraction to load test data"""
    def __init__(self):
        # Load User data
        data_file = codecs.open("./tests/test_data.json", "r", "utf-8").read()
        data_file = json.loads(data_file)
        self.user_data = data_file['user']
        self.list_data = data_file['list']
        self.list_items = data_file['items']


class TestUsers(TestDataLoader):

    def __init__(self):
        super(TestUsers, self).__init__()

    def create_user(self, user_data, status=200):
        """Convinience method to create a new user"""
        user_data = user_data
        res = app.post_json('/v1/users',
                            user_data,
                            status=status,
                            expect_errors=status != 200)
        return res

    def test_create_user(self):
        """Test POST for /v1/users"""
        user_data = self.user_data

        # Create a new user with all data
        user = self.create_user(user_data).json

        for key in self.user_data.keys():
            nt.assert_equals(user[key], self.user_data[key])
        nt.assert_true(user['id'] is not None)

        # Create a user with missing data
        resp = self.create_user({}, status=400)
        nt.assert_equals(resp.status_code, 400)

        # Create user with wrong data
        resp = self.create_user({"wrong_field": "crash!"}, status=400)
        nt.assert_equals(resp.status_code, 400)


    def test_get_users(self):
        """Test GET for /v1/users and /v1/users/<user_id>"""

        resp = app.get('/v1/users')
        nt.assert_equals(resp.status_code, 200)
        nt.assert_is_not_none(resp.json)

        user = resp.json.get('users')[0]

        # Get user with existing ID
        resp = app.get("/v1/users/{user_id}".format(user_id=user['id']))
        nt.assert_equals(resp.status_code, 200)

        # Check the data
        for key in self.user_data.keys():
            nt.assert_equals(user[key], self.user_data[key])
        nt.assert_true(user['id'] is not None)

        # Get non-existing user
        resp = app.get('/v1/users/{user_id}'.format(user_id=uuid.uuid4()))
        nt.assert_equals(resp.json, {})
        nt.assert_equals(resp.status_code, 200)
