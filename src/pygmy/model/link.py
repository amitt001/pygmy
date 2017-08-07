import binascii
import time

from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy import (Column, String, Integer,
                        Boolean, BigInteger, Unicode, DateTime)


class Link(Model):
    """Link"""

    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    long_url = Column(Unicode, index=True)
    # TODO pull values from long url
    protocol = Column(String(10), default='http://')
    domain = Column(String(300), )
    long_url_hash = Column(String(32), index=True)
    short_code = Column(Unicode, unique=True, index=True)
    description = Column(String(1000), default=None)
    hits_counter = Column(BigInteger, default=0)
    owner = Column(Integer, default='')
    # Not a password, just secret key. Its stored as plain text.
    secret_key = Column(String(12), default='')
    expire_after = Column(Integer, default=None)
    # This field tells wether this is a default or customized link
    # Custom link can have:
    # 1. custom short code, 2. expire_time, 3. secret key
    is_default = Column(Boolean, default=False)
    is_protected = Column(Boolean, default=False)
    is_disabled = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @staticmethod
    def generate_short_code(_, connection, target):
        # Check if a custom link
        is_default = True
        if target.is_protected or target.is_custom or target.expire_after:
            is_default = False
        # to resolve cyclic import
        from pygmy.helpers.link_helper import next_short_code
        table = Link.__table__
        if not target.short_code:
            short_code = next_short_code()
            connection.execute(
                table.update().where(
                    table.c.id == target.id).values(
                    short_code=short_code,
                    is_default=is_default
                )
            )

event.listen(Link, 'after_insert', Link.generate_short_code)


class LinkManager:
    """Link model manager"""

    def __init__(self, link=None):
        """Link object can also be passed to use helper functions.
        :param link:
        """
        self.link = link
        self.db = self.init_db_obj()
        self._BIG_INT = 999999999999919

    def __del__(self):
        if self.db:
            return
        self.db.commit()
        self.db.close()

    @dbconnection
    def init_db_obj(self, db):
        return db

    @property
    def created_at_epoch(self):
        """Retruns epoch in seconds."""
        return self.link.created_at.timestamp()

    @property
    def expire_at_epoch(self):
        if self.link and self.link.expire_after:
            return self.created_at_epoch + (self.link.expire_after * 60)
        return self._BIG_INT

    @dbconnection
    def disable(self, db):
        """Disable a link."""
        self.link.is_disabled = True
        self.link.is_default = False
        db.commit()

    def has_expired(self):
        """Check if the link has expired."""
        print(time.time(), self.expire_at_epoch)
        if not self.link.is_disabled and time.time() >= self.expire_at_epoch:
            self.disable()
            return True
        return False

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
        if kwargs.get('short_code'):
            self.link.short_code = kwargs.get('short_code')
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
        if kwargs.get('short_code'):
            query_dict['short_code'] = kwargs.get('short_code')
        query_dict['is_disabled'] = False
        return query_dict

    @dbconnection
    def click_counter(self, db):
        if self.link is None:
            return
        self.link.hits_counter += 1
        db.commit()

    @dbconnection
    def get(self, db, long_url, is_default=True):
        query_dict = dict(long_url_hash=self.crc32(long_url),
                          long_url=long_url,
                          is_default=is_default)
        link = db.query(Link).filter_by(**query_dict)
        if link.count() < 1:
            return None
        return link.one()

    @dbconnection
    def latest_default_link(self, db):
        """Returns latest non custom link"""
        return db.query(Link
                    ).filter_by(is_custom=False
                    ).order_by(Link.created_at.desc()
                    ).first()

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
        # q = str(
        # url.statement.compile(compile_kwargs={"literal_binds": True}))
        if url.count() < 1:
            return None
        # TODO: handle multiple in case of empty query dict
        self.link = url.one()
        return self.link

    @dbconnection
    def remove(self, db, long_url):
        """But why?"""
        pass
