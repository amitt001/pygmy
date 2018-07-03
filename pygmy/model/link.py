import time
import binascii
import datetime

from sqlalchemy import event, and_, or_, DDL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy import (Column, String, Integer, Boolean,
                        BigInteger, Unicode, DateTime)
from urllib.parse import urlparse

from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection, utcnow
from pygmy.exception.error import ShortURLUnavailable
from pygmy.model.clickmeta import ClickMeta


class Link(Model):
    """Link"""

    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    long_url = Column(Unicode(1000), index=True)
    # TODO pull values from long url
    protocol = Column(String(10), default='http://')
    domain = Column(String(300), )
    long_url_hash = Column(BigInteger, index=True)
    short_code = Column(Unicode(6), unique=True, index=True, default=None)
    description = Column(String(1000), default=None)
    owner = Column(Integer, default=None)
    clickmeta = relationship(
        ClickMeta, back_populates='link', cascade='delete')
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

    created_at = Column(DateTime(), server_default=utcnow())
    updated_at = Column(DateTime(), onupdate=utcnow())

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

# adding event to modify field `short_code` when using mysql
event.listen(
    Link.__table__,
    "after_create",
    DDL(
        "alter table {table} modify short_code varchar(6) "
        "CHARACTER SET utf8 COLLATE utf8_bin default null".format(
            table=Link.__tablename__
        )
    ).execute_if(dialect='mysql')
)

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
        # Not working
        if not self.db or 1:
            return
        self.db.commit()
        self.db.close()

    @dbconnection
    def __iter__(self, db):
        """Loop over object."""
        yield from db.query(Link).order_by(Link.id).all()

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

    @staticmethod
    def build_query_dict(**kwargs):
        """Build a dictionary from kwargs"""
        query_dict = dict()
        if kwargs.get('id'):
            query_dict['id'] = kwargs.get('id')
        if kwargs.get('short_code'):
            query_dict['short_code'] = kwargs.get('short_code')
        if kwargs.get('owner'):
            query_dict['owner'] = kwargs.get('owner')
        if kwargs.get('short_code'):
            query_dict['short_code'] = kwargs.get('short_code')
        if kwargs.get('is_custom') is not None:
            query_dict['is_custom'] = kwargs.get('is_custom')
        if kwargs.get('is_protected') is not None:
            query_dict['is_protected'] = kwargs.get('is_protected')
        # TODO: handle disabled
        return query_dict

    @dbconnection
    def disable(self, db):
        """Disable a link."""
        self.link.is_disabled = True
        self.link.is_default = False
        db.commit()

    def has_expired(self):
        """Check if the link has expired."""
        if self.link and self.link.is_disabled:
            return True
        if self.link and (time.time() >= self.expire_at_epoch):
            self.disable()
            return True
        return False

    @staticmethod
    def crc32(long_url):
        if not urlparse(long_url).scheme:
            long_url = 'http://{}'.format(long_url)
        return binascii.crc32(str.encode(long_url))

    @property
    @dbconnection
    def short_links(self, db):
        yield from db.query(Link).order_by(Link.id).all()

    @dbconnection
    def add(self, db, long_url, **kwargs):
        # TODO: verify/escape input
        if db.bind.name == 'mysql':
            kwargs['created_at'] = datetime.datetime.utcnow()
            kwargs['updated_at'] = datetime.datetime.utcnow()
        if not urlparse(long_url).scheme:
            long_url = 'http://{}'.format(long_url)
        self.link = Link(long_url=long_url,
                         long_url_hash=self.crc32(long_url), **kwargs)
        db.add(self.link)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ShortURLUnavailable('Short URL already taken or unavailable')
        return self.link

    @dbconnection
    def update(self, db, **kwargs):
        if self.link is None:
            self.link = self.find(**kwargs)
        # Get update fields.
        if db.bind.name == 'mysql':
            kwargs['updated_at'] = datetime.datetime.utcnow()
        if kwargs.get('short_code'):
            self.link.short_code = kwargs.get('short_code')
        if kwargs.get('description'):
            self.link.description = kwargs.get('description')
        db.commit()
        return self.link

    @dbconnection
    def get(self, db, long_url, is_default=True):
        if not urlparse(long_url).scheme:
            long_url = 'http://{}'.format(long_url)
        query_dict = dict(long_url_hash=self.crc32(long_url),
                          long_url=long_url,
                          is_default=is_default)
        url = db.query(Link).filter_by(**query_dict)
        if url.count() < 1:
            return None
        self.link = url.first()
        return self.link

    @dbconnection
    def get_by_code(self, db, short_code):
        self.link = db.query(Link).filter(
                        Link.short_code == short_code).first()
        return self.link

    @dbconnection
    def get_by_id(self, db, link_id):
        return db.query(Link).filter_by(id=link_id).first()

    @dbconnection
    def get_by_owner(self, db, owner_id):
        yield from db.query(Link).filter(
            Link.owner == owner_id).order_by(Link.id).all()

    @dbconnection
    def link_clickmeta(self, db):
        return self.link.clickmeta

    @property
    @dbconnection
    def short_codes_list(self, db):
        """Return all short codes list"""
        result_set = db.query(Link)
        for r in result_set.values(Link.short_code):
            yield r[0]

    @property
    @dbconnection
    def long_links_list(self, db):
        """Return all long links list"""
        result_set = db.query(Link)
        for r in result_set.values(Link.long_url):
            yield r[0]

    @property
    @dbconnection
    def disabled_links(self, db):
        result_set = db.query(Link).filter(Link.is_disabled == 1)
        yield from result_set.order_by(Link.id).all()

    @dbconnection
    def latest_default_link(self, db):
        """Returns latest non custom link"""
        return db.query(Link).filter(and_(
            Link.is_custom.is_(False),
            Link.short_code.isnot(None),
            Link.short_code != ''
        )).order_by(Link.id.desc()).first()

    @dbconnection
    def find(self, db, **kwargs):
        """Find by filter params. Order of query_dict is important. In case
        of query by `long_url` first calculate crc32 hash and query it before
        long_url query for performance optimization.
        """
        query_dict = dict()
        long_url = kwargs.get('long_url')
        if long_url:
            if not urlparse(long_url).scheme:
                long_url = 'http://{}'.format(long_url)
            query_dict['long_url_hash'] = self.crc32(long_url)
            query_dict['long_url'] = long_url
        query_dict.update(self.build_query_dict(**kwargs))
        # build sqlalchmey and query
        query = [getattr(Link, k) == v for k, v in query_dict.items()]
        url = db.query(Link).filter(and_(*query))
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
