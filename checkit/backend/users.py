import uuid

from sqlalchemy import Column
from sqlalchemy.types import String, Integer

from checkit.utils import sql

class User(sql.Base):
    """User object to represent a user database table"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys}


class UsersStore(sql.SQLBackend):
    """Helper clase to manage User(s) common opperations"""

    def __init__(self):
        pass

    def setup(self, database):
        super(UsersStore, self).__init__(database, sql.Base)

    @sql.with_own_session
    def get_users(self, session):
        users = session.query(User).all()
        return users

    @sql.with_own_session
    def get_user(self, session, user_id):
        user = session.query(User).filter_by(id=user_id).first()
        return user

    @sql.with_own_session
    def create_user(self, session, user_data):
        user = User(**user_data)
        session.add(user)
        session.commit()

        return user
