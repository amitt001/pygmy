import os

from configparser import ConfigParser

_CONFIG_ENV_VAR = 'PYGMY_CONFIG_FILE'


class Configuration:
    def __init__(self):
        # default sqlite3
        # TODO: Take this from cfg file
        self.cfg = None
        self.database = {}
        self.debug = False
        self.schema = None
        self.host = None
        self.port = None
        self.webservice_url = None

    def _read_cfg(self):
        self.cfg = ConfigParser()
        self.cfg.read(os.environ[_CONFIG_ENV_VAR])

    def initialize(self):
        """Called from when the program is initialized and config
        path is loaded."""
        # TODO: handle automatic assignment
        self._read_cfg()
        self.database = dict(self.cfg['database'].items())
        self.debug = (self.cfg['pygmy']['debug'] == 'True')
        self.schema = self.cfg['pygmy']['schema']
        self.host = self.cfg['pygmy']['host']
        self.port = self.cfg['pygmy']['port']
        self.webservice_url = "{0}://{1}:{2}".format(
            self.schema, self.host, self.port)

