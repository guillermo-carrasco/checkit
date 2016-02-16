import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String, Boolean

from checkit.utils import sql

class TodoList(sql.Base):
    """Object to represent a TODO list in the database"""

    __tablename__ = 'todo_lists'

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    description = Column(String(250))

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys}


class TodoItem(sql.Base):
    """Object to represent a TodoItem within a TODO list"""

    __tablename__ = 'todo_items'
    id = Column(UUID, primary_key=True)
    todo_list_id = Column(UUID, ForeignKey("todo_lists.id"), nullable=False)
    description = Column(String(100), nullable=False)
    checked = Column(Boolean, nullable=False)

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys}


class TodoListsStore(sql.SQLBackend):
    """Helper clase to manage TodoLists(s) common opperations"""

    def __init__(self):
        pass

    def setup(self, database):
        super(TodoListsStore, self).__init__(database, sql.Base)

    @sql.with_own_session
    def get_todo_lists(self, session, user_id):
        td_lists = session.query(TodoList).filter_by(user_id=user_id)
        return td_lists
