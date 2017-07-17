from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from pygmy.config import config


class BaseDatabase:
    """Use this as a base databse for other databases"""

    def __init__(self):
        self.engine = None
        self.url = None
        self.store = None

    def _prepare(self, url):
        """Pre processing tasks for db."""
        pass

    def commit(self):
        self.store.commit()

    def abort(self):
        self.store.rollback()

    def initialize(self, debug=False):
        self.url = config.database['url']
        self._prepare(self.url)
        self.engine = create_engine(self.url, echo=debug)
        session = sessionmaker(bind=self.engine)
        self.store = session()
        self.store.commit()


Model = declarative_base()
