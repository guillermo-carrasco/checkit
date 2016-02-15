import os
import unittest

from checkit.server import api
from checkit.backend.users import User

class TestBase(unittest.TestCase):
    """Base class for the tests."""

    def setUp(self):
        """Set up test database"""
        self.app = api.get_app()
        # Configure the app to work on a test database
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/checkit_db_test.db'
        # And delete any previous test database
        try:
            os.remove('/tmp/checkit_db_test.db')
        except OSError:
            pass
        self.db = api.get_db()
        self.db.create_all()

    def tearDown(self):
        """Remove test database if it was created"""
        try:
            os.remove('/tmp/checkit_db_test.db')
        except OSError:
            pass



class TestUser(TestBase):
    """Test set for the user database"""

    def test_1_user_creation(self):
        """Create a user and check its returned by the Database Adapter"""
        user = User('test_db')
        self.db.session.add(user)
        self.db.session.commit()
        self.assertTrue(User.query.filter_by(username='test_db').first().username == 'test_db')
