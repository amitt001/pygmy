import binascii

from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection
from pygmy.core.hashdigest import HashDigest
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy import (Column, String, Integer,
                        Boolean, BigInteger, Unicode, DateTime)


class Link(Model):
    """Link"""

    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    long_url = Column(Unicode, unique=True, index=True)
    # TODO pull values from long url
    protocol = Column(String(10), default='http://')
    domain = Column(String(300), )
    long_url_hash = Column(String(32), index=True)
    short_url = Column(Unicode, index=True)
    description = Column(String(1000), default=None)
    hits_counter = Column(BigInteger, default=0)
    owner = Column(Integer, default='')
    # Not a password, just secret key. Its stored as plain text.
    secret_key = Column(String(12), default='')
    is_protected = Column(Boolean, default=False)
    is_disabled = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @staticmethod
    def generate_short_url(_, connection, target):
        table = Link.__table__
        if target.short_url is None:
            short_url = HashDigest().shorten(target.id)
            connection.execute(
                table.update().where(
                    table.c.id == target.id).values(
                    short_url=short_url
                )
            )

event.listen(Link, 'after_insert', Link.generate_short_url)


class LinkManager:
    """Link model manager"""

    def __init__(self):
        self.link = None

    @staticmethod
    def crc32(long_url):
        return binascii.crc32(str.encode(long_url))

    @dbconnection
    def add(self, db, long_url, **kwargs):
        # TODO: verify/escape input
        self.link = Link(long_url=long_url,
                         long_url_hash=self.crc32(long_url), **kwargs)
        db.add(self.link)
        db.commit()
        return self.link

    @dbconnection
    def update(self, db, **kwargs):
        if self.link is None:
            self.link = self.find(**kwargs)
        # Get update fields.
        if kwargs.get('short_url'):
            self.link.short_url = kwargs.get('short_url')
        if kwargs.get('description'):
            self.link.description = kwargs.get('description')
        if kwargs.get('hits_counter'):
            self.link.hits_counter = kwargs.get('hits_counter')
        db.commit()
        return self.link

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
    def click_counter(self, db):
        if self.link is None:
            return
        self.link.hits_counter += 1
        db.commit()

    @dbconnection
    def get(self, db, long_url):
        query_dict = dict(long_url_hash=self.crc32(long_url),
                          long_url=long_url)
        link = db.query(Link).filter_by(**query_dict)
        if link.count() < 1:
            return None
        return link.one()

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
        self.link = url.one()
        return self.link

    @dbconnection
    def remove(self, db, long_url):
        """But why?"""
        pass
