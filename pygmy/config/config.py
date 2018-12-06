import os

from configparser import ConfigParser, NoSectionError

_CONFIG_ENV_VAR = 'PYGMY_CONFIG_FILE'


class Configuration:
    def __init__(self):
        # default sqlite3
        # TODO: Take this from cfg files
        self.default_config_path = 'pygmy/config/pygmy.cfg'
        self.cfg = None
        self.debug = False
        self.schema = None
        self.host = None
        self.port = None
        self.secret = None
        self.logging = None
        self.webservice_url = None
        self.database = None
        self.initialize()

    def _read_cfg(self):
        self.cfg = ConfigParser()
        self.cfg.read(os.environ.get(_CONFIG_ENV_VAR, self.default_config_path))

    def __getattr__(self, name):
        """Add sections dynamically. With this no need to define
        each sections in initialize() method.

        TODO: config.host should be accessed as config.rest['host'].
        Remove initialize method."""
        if self.cfg is None:
            self._read_cfg()
        try:
            return dict(self.cfg[name].items())
        except KeyError:
            return NoSectionError('No {} section found'.format(name))

    def initialize(self):
        """Called from when the program is initialized and config
        path is loaded."""
        # TODO: handle automatic assignment
        self._read_cfg()
        self.debug = (self.cfg['pygmy']['debug'] == 'True')
        self.database = dict(self.cfg['database'].items())
        self.schema = self.cfg['pygmy']['schema']
        self.host = self.cfg['pygmy']['host']
        self.port = self.cfg['pygmy']['port']
        self.secret = self.cfg['pygmy']['flask_secret']
        self.logging = self.cfg['logging']
        self.webservice_url = "{0}://{1}:{2}".format(
            self.schema, self.host, self.port)

        if self.database['engine'] == 'sqlite3':
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = self.database.get('sqlite_data_dir') or 'data'
            file_name = self.database.get('sqlite_db_file_name') or 'pygmy.db'
            sqlite_path = root_dir + '/' + data_dir + '/' + file_name
            self.database['url'] = 'sqlite:///{}'.format(sqlite_path)
