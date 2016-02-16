from checkit.utils import sql, log
import users as users_backend

users = users_backend.UsersStore()

def setup_stores(db_url):
    """Initialize backend stores"""
    users.setup(db_url)
