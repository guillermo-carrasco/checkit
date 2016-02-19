"""SQLAlchemy abstractions to ease DB managment"""

import logging

import functools

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

LOG = logging.getLogger(__name__)


def with_own_session(f):
    """Decorator to provide a new SQLAlchemy session to the method wrapped"""
    def wrapper(self, *args, **kwargs):
        return self.with_self_and_session(f)(self, *args, **kwargs)
    return wrapper


def create_declarative_base():
    base = declarative_base()
    return base


class SQLBackend(object):

    def __init__(self, db_string, base):
        if db_string:
            self.engine = None
            self.Base = base
            self.Session = sessionmaker(autocommit=False, expire_on_commit=False)
            self.setup_session(db_string)

    def with_self_and_session(self, f):
        """Useful wrapper to manage SQLAlchemy sessions.

        When a method is decorated with @with_self_and_session a new session will be created to execute
        that method. At the end it will close the session automatically. If any error occurs, the session
        will be rolled back.
        """
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            session = self.Session()
            try:
                return f(args[0], session, *(args[1:]), **kwargs)
            except:
                session.rollback()
                raise
            finally:
                session.expunge_all()
                session.close()
        return wrapper

    def setup_session(self, db_string=None):
        self._create_engine(db_string)
        self.Session.configure(bind=self.engine)

    def reset(self):
        """Reset all tables"""
        self.Base.metadata.drop_all(bind=self.engine)
        self.Base.metadata.create_all(bind=self.engine)

    def create_tables(self):
        self.Base.metadata.create_all(bind=self.engine)

    def bootstrap(self):
        """Creates database and tables"""
        database = self.engine.url.database
        engine = create_engine(self.engine.url)
        connection = engine.connect()
        connection.execute("COMMIT")

        try:
            connection.execute("CREATE DATABASE %s" % database)
        except Exception as e:
            LOG.warn("Database {} was already created, skipping".format(database))
            pass
        finally:
            connection.close()

        LOG.info("Creating databases")
        self.Base.metadata.create_all(bind=self.engine)

    def _create_engine(self, db_string=None):
        if self.engine:
            return

        self.engine = create_engine(db_string, echo=False)


Base = create_declarative_base()
