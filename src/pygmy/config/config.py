import os

from configparser import ConfigParser, NoSectionError

_CONFIG_ENV_VAR = 'PYGMY_CONFIG_FILE'


class Configuration:
    def __init__(self):
        # default sqlite3
        # TODO: Take this from cfg files
        self.cfg = None
        self.debug = False
        self.schema = None
        self.host = None
        self.port = None
        self.secret = None
        self.webservice_url = None

    def _read_cfg(self):
        self.cfg = ConfigParser()
        self.cfg.read(os.environ[_CONFIG_ENV_VAR])

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
        self.schema = self.cfg['pygmy']['schema']
        self.host = self.cfg['pygmy']['host']
        self.port = self.cfg['pygmy']['port']
        self.secret = self.cfg['rest']['flask_secret']
        self.webservice_url = "{0}://{1}:{2}".format(
            self.schema, self.host, self.port)

