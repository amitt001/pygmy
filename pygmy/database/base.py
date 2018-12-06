import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from pygmy.config import config
from pygmy.core.logger import log


class BaseDatabase:
    """Use this as a base databse for other databases"""

    def __init__(self):
        self.engine = None
        self._db_url = None
        self.store = None

    def _prepare(self, url):
        """Pre processing tasks for db."""
        pass

    def commit(self):
        self.store.commit()

    def abort(self):
        self.store.rollback()

    # TODO: Probs, should be done in config
    @property
    def db_url(self):
        """Gets the url from config file pygmy.cfg and then look up for
        following enviorment variable. If found, replcases the values

        - DB_HOST
        - DB_PORT
        - DB_USER
        - DB_PASS
        - DB_DBNAME

        The reason for two ways to get DB url is support for both CLI
        based runs and ducker-compose/kubernetes based runs
        """
        if self._db_url is not None:
            return self._db_url

        self._db_url = config.database['url']
        if config.database['engine'] == 'sqlite3':
            return self._db_url

        # As in case of mysql we use pymysql, modify engine here
        if config.database['engine'] == 'mysql':
            engine = 'mysql+pymysql'
        else:
            engine = config.database['engine']


        # Get environment variables
        host, port, user, password, db_name = (
                os.environ.get('DB_HOST'), os.environ.get('DB_PORT'),
                os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'),
                os.environ.get('DB_NAME'))

        if any([host, port, user, password, db_name]):
            log.info('Replacing config value by environment variable')

        url_kw_params = {
            'engine': engine,
            'user': user or config.database['user'],
            'password': password or config.database['password'],
            'host': host or config.database['host'],
            'port': port or config.database['port'],
            'db_name': db_name or config.database['db_name']
        }
        try:
            self._db_url = self._db_url.format(**url_kw_params)
        except KeyError as err:
            # Raised if one of the config is not passed
            raise KeyError('Key: {} not set in config file'.format(err))


    def initialize(self, debug=False):
        log.info('DB URL: {}'.format(self.db_url))
        self._prepare(self.db_url)
        self.engine = create_engine(self.db_url, echo=debug)
        session = sessionmaker(bind=self.engine)
        self.store = session()
        self.store.commit()


Model = declarative_base()
