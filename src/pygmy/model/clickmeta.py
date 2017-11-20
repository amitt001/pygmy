import datetime

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String, DateTime, ForeignKey
from urllib.parse import urlparse

from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection, utcnow


class ClickMeta(Model):
    __tablename__ = 'clickmeta'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # TODO AMIT: should be enum
    link_id = Column(Integer, ForeignKey('link.id'))
    link = relationship(
        'Link', back_populates='clickmeta', foreign_keys=[link_id])
    country = Column(String(5), nullable=True)
    referrer = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=utcnow())


class ClickMetaManager:
    """Click meta manager"""

    def __init__(self):
        self.clickmeta = None
        self._oldest_link_date = None
        self._referrer_aggregate = None
        self._country_aggregate = None
        self._date_aggregate = None

    @staticmethod
    def _format_referrer(referrer):
        ref = urlparse(referrer)
        if not ref.netloc:
            return None
        referrer = "{}://{}{}".format(
            ref.scheme or 'http', ref.netloc, ref.path)
        if len(referrer) > 100:
            return None
        return referrer

    @staticmethod
    def _date_display_format(base):
        date_format_map = dict(minute="%H:%M",
                               hour="%H:00",
                               day="%m-%d",
                               month="%Y-%m-%d")
        return date_format_map.get(base)

    @staticmethod
    def psql_date_format(date_str):
        psql_format = date_str
        date_arg_map = {
            '%Y': 'YYYY',
            '%m': 'MM',
            '%d': 'DD',
            '%H': 'HH24',
            '%M': 'MI',
            '%S': 'SS'
        }
        for dt_arg, dt_val in date_arg_map.items():
            psql_format = psql_format.replace(dt_arg, dt_val)
        return psql_format

    @staticmethod
    def mysql_date_format(date_str):
        psql_format = date_str
        date_arg_map = {
            '%M': '%i',
        }
        for dt_arg, dt_val in date_arg_map.items():
            psql_format = psql_format.replace(dt_arg, dt_val)
        return psql_format

    @property
    def past_30th_date(self):
        d = (datetime.datetime.utcnow() - datetime.timedelta(days=30))
        day_30 = d.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        return day_30

    @dbconnection
    def add(self, db, link_id, country, referrer, user_agent=None):
        referrer = self._format_referrer(referrer)
        insert_values = dict(link_id=link_id,
                             country=country,
                             referrer=referrer)
        if db.bind.name == 'mysql':
            insert_values['created_at'] = datetime.datetime.utcnow()
        self.clickmeta = ClickMeta(**insert_values)
        db.add(self.clickmeta)
        db.commit()
        return self.clickmeta

    @dbconnection
    def get_by_link(self, db, link_id):
        """Pass link id and get clickmeta object"""
        yield db.query(ClickMeta).find(link_id=link_id).all()

    @dbconnection
    def link_hit_count(self, db, params):
        """Get hit count for the passed link id
        :param db:
        :param params:
        :return:
        """
        qry = text("SELECT COUNT(*) FROM clickmeta WHERE link_id=:link_id")
        return db.execute(qry, params).first()[0]

    @dbconnection
    def country_aggregate(self, db, params):
        """Country aggregate for the passed link id
        :param db:
        :param params:
        :return:
        """
        if self._country_aggregate is None:
            qry = text("""
                SELECT COALESCE(country, 'others'), COUNT(*)
                From clickmeta
                WHERE link_id=:link_id
                GROUP BY country
                ORDER BY count(*) DESC""")
            self._country_aggregate = dict(db.execute(qry, params).fetchall())
        return self._country_aggregate

    @dbconnection
    def referrer_aggregate(self, db, params):
        """Referrer aggregate for the passed link id
        :param db:
        :param params:
        :return:
        """
        if self._referrer_aggregate is None:
            qry = text("""
                SELECT COALESCE(referrer, 'others'), COUNT(*) FROM clickmeta
                WHERE link_id=:link_id
                GROUP BY referrer
                ORDER BY count(*) DESC""")
            self._referrer_aggregate = dict(db.execute(qry, params).fetchall())
        return self._referrer_aggregate

    @dbconnection
    def date_aggregate(self, db, date_part, params, base):
        """Datetime aggregation for a link id.
        :param db:
        :param date_part:
        :param params:
        :param base:
        :return:
        """
        if self._date_aggregate is None:
            qry = text("""
                SELECT {} AS click_on, COUNT(*)
                FROM clickmeta
                WHERE link_id=:link_id AND created_at >= :created_at
                GROUP BY click_on
                ORDER BY click_on DESC
                """.format(date_part))
            data = db.execute(qry, params).fetchall()
            if base == 'month':
                self._date_aggregate = dict(
                    (datetime.datetime.strptime(
                        k, '%Y-%m-%d').strftime('%d %b, %Y'), val)
                    for k, val in data)
            if base == 'day':
                self._date_aggregate = dict(
                    (datetime.datetime.strptime(
                        k, '%m-%d').strftime('%d %b'), val)
                    for k, val in data)
            else:
                self._date_aggregate = dict(data)
        return self._date_aggregate

    @dbconnection
    def oldest_click_date(self, db, params):
        """Get the oldest click info date for a link.
        :param db:
        :param params:
        :return: date str
        """
        if self._oldest_link_date is None:
            qry = text("""
                SELECT created_at FROM clickmeta
                WHERE link_id=:link_id
                ORDER BY created_at ASC
                LIMIT 1
                """)
            link_date = db.execute(qry, params).first()
            if link_date is None:
                return None
            link_date = link_date[0]
            if isinstance(link_date, datetime.datetime):
                link_date = link_date.strftime("%Y-%m-%d %H:%M:%S")
            self._oldest_link_date = link_date
        return self._oldest_link_date

    @dbconnection
    def click_stats(self, db, link_id):
        """Function to get click aggregation data based on:
            1. Country
            2. Referrer
            3. Datetime: It can be based on minute, hour, or days depending
                on how old the link clickstats are.

        :param db:
        :param link_id:
        :return: dict
        """
        bind_param = dict(link_id=link_id,
                          created_at=self.past_30th_date)
        assert db.bind.name in ['sqlite', 'mysql', 'postgresql']
        db_date_function_mapper = dict(sqlite='STRFTIME',
                                       postgresql='TO_CHAR',
                                       mysql='DATE_FORMAT')
        date_func = db_date_function_mapper.get(db.bind.name)
        # if None, it means no record found for the link
        oldest_link_date = self.oldest_click_date(bind_param)
        if oldest_link_date is None:
            return {}
        base = time_base(oldest_link_date)
        date_format = self._date_display_format(base)
        if db.bind.name == 'postgresql':
            date_format = self.psql_date_format(date_format)
            date_part = "{}(created_at, '{}')".format(date_func, date_format)
        elif db.bind.name == 'mysql':
            date_format = self.mysql_date_format(date_format)
            date_part = "{}(created_at, '{}')".format(date_func, date_format)
        else:
            date_part = "{}('{}', created_at)".format(date_func, date_format)
        return dict(
            hits=self.link_hit_count(bind_param),
            country_hits=self.country_aggregate(bind_param),
            referrer_hits=self.referrer_aggregate(bind_param),
            timestamp_hits=self.date_aggregate(date_part, bind_param, base),
            time_base=base
        )


def time_base(date_str):
    """Returns base for the time string `date_str` passed.

    :param date_str: str
    :return: str
    """
    old_link_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    time_delta = datetime.datetime.utcnow() - old_link_date
    delta_seconds = time_delta.total_seconds()
    if (delta_seconds / (60*60)) < 1:
        return 'minute'
    elif (delta_seconds / (60*60*24)) < 1:
        return 'hour'
    elif (delta_seconds / (60*60*24*30)) < 1:
        return 'day'
    else:
        return 'month'
