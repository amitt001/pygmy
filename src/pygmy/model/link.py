import binascii

from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection
from sqlalchemy.sql import func
from sqlalchemy import (
    Column, String, Integer, BigInteger, Unicode, DateTime)


class Link(Model):
    """Link"""

    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    long_url = Column(Unicode, unique=True, index=True)
    long_url_hash = Column(String(32), index=True)
    short_url = Column(Unicode, index=True)
    description = Column(String(1000), default=None)
    hits_counter = Column(BigInteger, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LinkManager:
    """Link model manager"""

    def __init__(self):
        self.url = None

    @staticmethod
    def crc32(long_url):
        return binascii.crc32(str.encode(long_url))

    @dbconnection
    def add(self, db, long_url, **kwargs):
        # TODO: verify/escape input
        self.url = Link(long_url=long_url,
                        long_url_hash=self.crc32(long_url), **kwargs)
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

    @staticmethod
    def build_query_dict(**kwargs):
        """Build a dictionary from kwargs"""
        query_dict = dict()
        if kwargs.get('id'):
            query_dict['id'] = kwargs.get('id')
        if kwargs.get('short_url'):
            query_dict['short_url'] = kwargs.get('short_url')
        return query_dict

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
        """Find by filter params. Order of query_dict is important. In case
        of query by `long_url` first calculate crc32 hash and query it before
        long_url query for performance optimization.
        """
        query_dict = dict()
        if kwargs.get('long_url'):
            query_dict['long_url_hash'] = self.crc32(kwargs.get('long_url'))
            query_dict['long_url'] = kwargs.get('long_url')
        query_dict.update(self.build_query_dict(**kwargs))
        url = db.query(Link).filter_by(**query_dict)
        if url.count() < 1:
            return None
        return url.one()

    @dbconnection
    def remove(self, db, long_url):
        """But why?"""
        pass


