"""SQLAlchemy abstractions to ease DB managment"""

import logging

import functools

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

LOG = logging.getLogger(__name__)


def with_own_session(f):
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

    def flush(self):
        for tbl in reversed(self.Base.metadata.sorted_tables):
            self.engine.execute(tbl.delete())

    def reset(self):
        self.Base.metadata.drop_all(bind=self.engine)
        self.Base.metadata.create_all(bind=self.engine)

    def create_tables(self):
        self.Base.metadata.create_all(bind=self.engine)

    def bootstrap(self):
        ''' Creates database and tables'''
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

    def ping(self):
        session = self.Session()
        ping_response = session.execute('select 1').fetchall()
        session.close()
        return ping_response


Base = create_declarative_base()
