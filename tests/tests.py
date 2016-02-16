import codecs
import copy
import json
import os

import nose.tools as nt

from webtest import TestApp

import checkit.server.api as api
from checkit.backend import setup_stores, users, todo_lists

app = None

def setup(module):
    """Set up testing environment by flushing and populating the test database"""
    DB_URI = os.environ.get('TEST_DB_URI', 'sqlite:////tmp/checkit_db.db')
    setup_stores(DB_URI)
    users.bootstrap()
    users.reset()
    todo_lists.bootstrap()
    todo_lists.reset()

    app = api.app
    module.app = TestApp(app)


class TestBase(object):
    """Base Test class to reset the database for each test"""

    def setup(self):
        users.flush()
        todo_lists.flush()
        # Load User data
        data_file = codecs.open("./tests/test_data.json", "r", "utf-8").read()
        data_file = json.loads(data_file)
        self.user_data = data_file['user']
        self.list_data = data_file['list']
        self.list_item_items = data_file['item']

    def create_user(self, user_data=None, status=200):
        user_data = user_data or self.user_data
        res = app.post_json('/v1/users',
                            user_data,
                            status=status,
                            expect_errors=status != 200)
        return res


class TestUsers(TestBase):

    def test_create_user(self):
        user = self.create_user().json
        for key in self.user_data.keys():
            nt.assert_equals(user[key], self.user_data[key])
        nt.assert_true(user['id'] is not None)
