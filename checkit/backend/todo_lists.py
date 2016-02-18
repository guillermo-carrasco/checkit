import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, subqueryload
from sqlalchemy.types import String, Boolean, Integer

from checkit.utils import sql

class TodoList(sql.Base):
    """Object to represent a TODO list in the database"""

    __tablename__ = 'todo_lists'

    id = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(250), nullable=False)
    items = relationship("TodoItem", cascade="all, delete-orphan")

    def to_dict(self):
        keys = self.__table__.c.keys()
        todo_list = {k: getattr(self, k) for k in keys}
        if 'items' in self.__dict__:
            todo_list['items'] = [item.to_dict() for item in self.items]
        return todo_list


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
        td_lists = session.query(TodoList) \
                          .options(subqueryload(TodoList.items)) \
                          .filter_by(user_id=user_id) \
                          .all()
        return td_lists

    @sql.with_own_session
    def create_todo_list(self, session, list_data, user_id):
        todo_list = TodoList(**list_data)
        todo_list.id = str(uuid.uuid4())
        todo_list.user_id = user_id
        session.add(todo_list)
        session.commit()

        return todo_list

    @sql.with_own_session
    def delete_todo_list(self, session, list_id):
        todo_list = session.query(TodoList).filter_by(id=list_id).first()
        session.delete(todo_list)
        session.commit()
        return True


    @sql.with_own_session
    def get_user_todo_list(self, session, list_id):
        todo_list = session.query(TodoList).filter_by(id=list_id).first()
        return todo_list

    @sql.with_own_session
    def get_list_items(self, session, list_id):
        items = session.query(TodoItem).filter_by(todo_list_id=list_id)
        return items

    @sql.with_own_session
    def create_item(self, session, todo_list_id, item_data):
        item = TodoItem(**item_data)
        item.id = str(uuid.uuid4())
        item.todo_list_id = todo_list_id
        item.checked = False
        session.add(item)
        session.commit()

        return item

    @sql.with_own_session
    def get_item(self, session, item_id):
        item = session.query(TodoItem).filter_by(id=item_id).first()
        return item

    @sql.with_own_session
    def update_item(self, session, item_data):
        item = session.query(TodoItem).filter_by(id=item_data.get('id')).update(item_data)
        session.commit()

        # If update was successful, 1 should be returned (the number of items updated)
        if item:
            return session.query(TodoItem).filter_by(id=item_data.get('id')).first()
        else:
            return None
