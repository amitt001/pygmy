from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection
from sqlalchemy.sql import func
from sqlalchemy import (
    Column, String, Integer, BigInteger, Unicode, DateTime)


class URL(Model):
    """URL"""

    __tablename__ = 'url'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_url = Column(Unicode, unique=True)
    short_url = Column(Unicode)
    description = Column(String(1000), default=None)
    hits_counter = Column(BigInteger, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class URLManager:
    """URL model manager"""

    def __init__(self):
        self.url = None

    @dbconnection
    def add(self, db, full_url, **kwargs):
        # TODO: verify/escape input
        self.url = URL(full_url=full_url, **kwargs)
        db.add(self.url)
        db.commit()
        return self.url

    @dbconnection
    def update(self, db, **kwargs):
        if self.url is None:
            self.url = self.find(**kwargs)
        # Get update fields.
        if kwargs.get('short_url'):
            self.url.short_url = kwargs.get('short_url')
        if kwargs.get('description'):
            self.url.description = kwargs.get('description')
        if kwargs.get('hits_counter'):
            self.url.hits_counter = kwargs.get('hits_counter')
        db.commit()
        return self.url

    @dbconnection
    def incr_counter(self, db):
        if self.url is None:
            return
        self.url.hits_counter += 1
        db.commit()

    @dbconnection
    def decr_counter(self, db):
        if self.url is None:
            return
        self.url.hits_counter -= 1
        db.commit()

    @dbconnection
    def find(self, db, **kwargs):
        """Find by filter patams"""
        query_dict = dict()
        if kwargs.get('id'):
            query_dict['id'] = kwargs.get('id')
        if kwargs.get('short_url'):
            query_dict['short_url'] = kwargs.get('short_url')
        if kwargs.get('full_url'):
            query_dict['full_url'] = kwargs.get('full_url')
        url = db.query(URL).filter_by(**query_dict)
        if url.count() < 1:
            return None
        return url.one()

    @dbconnection
    def remove(self, db, full_url):
        """But why?"""
        pass


