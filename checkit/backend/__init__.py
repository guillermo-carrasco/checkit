from checkit.utils import sql, log
import users as users_backend
import todo_lists as todo_lists_backend

users = users_backend.UsersStore()
todo_lists = todo_lists_backend.TodoListsStore()

def setup_stores(db_url):
    """Initialize backend stores"""
    users.setup(db_url)
    todo_lists.setup(db_url)
    todo_lists.bootstrap()
