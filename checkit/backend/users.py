import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import String, Integer

from checkit.utils import sql

class User(sql.Base):
    """User object to represent a user database table"""

    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    name = Column(String(80))
    email = Column(String(200))
    gh_token = Column(String(200), nullable=False)

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
        """Retrieve ll users from the database"""
        users = session.query(User).all()
        return users

    @sql.with_own_session
    def get_user(self, session, user_id):
        """Retrun user with id <user_id> from the database"""
        user = session.query(User).filter_by(id=user_id).first()
        return user

    @sql.with_own_session
    def get_user_by_token(self, session, gh_token):
        """Retrun user with token <gh_token> from the database"""
        user = session.query(User).filter_by(gh_token=gh_token).first()
        return user

    @sql.with_own_session
    def create_user(self, session, user_data):
        """Create a new user in the database"""
        if not 'id' in user_data:
            user_data['id'] = str(uuid.uuid4())
        user = User(**user_data)
        session.add(user)
        session.commit()

        return user

    @sql.with_own_session
    def update_user(self, session, user_data):
        """Updates existing user's information"""
        user = session.query(User).filter_by(id=user_data.get('id')).update(user_data)
        session.commit()
