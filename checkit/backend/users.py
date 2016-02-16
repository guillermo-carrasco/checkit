from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String

from checkit.utils import sql

class User(sql.Base):
    """User object to represent a user database table"""

    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    name = Column(String(80), unique=True)

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
        print users
        return users
