import os
from unittest import TestCase

from pygmy.core.initialize import initialize
from pygmy.app.link import shorten, unshorten
from pygmy.config import config


class URLShortenUnshortenTestCases(TestCase):
    """Tests to shorten-unshorten a long url"""

    DBDir = None

    @classmethod
    def setUp(self):
        self.long_url = 'https://github.com'

    @classmethod
    def setupClass(cls):
        # Do the real setup
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_path = currdir + '/pygmy_test.cfg'
        initialize(config_path)
        if config and config.database['engine'] == 'sqlite3':
            from urllib.parse import urlparse
            cls.DBDir = urlparse(config.database['url']).path

    @classmethod
    def tearDownClass(cls):
        if cls.DBDir is None or not os.path.exists(cls.DBDir):
            return
        os.remove(cls.DBDir)

    def test_config(self):
        assert config is not None
        assert config.db is not None
        # sqlite only test, remove it later
        assert self.DBDir is not None

    def test_long_url_shorten(self):
        data = shorten(self.long_url)
        assert isinstance(data, dict) is True
        print(data)
        assert data['short_code'] == 'b'
        assert data['is_disabled'] is False
        assert data['is_protected'] is False
        assert data['is_custom'] is False

    def test_custom_short_url(self):
        short_code = 'test'
        data = shorten(self.long_url, short_code=short_code)
        assert data['short_code'] == short_code
        assert data['is_custom'] is True
        udata = unshorten(short_url=short_code)
        assert udata['long_url'] == self.long_url

    def test_secret_short_url(self):
        secret_key = 'safe'
        data = shorten(self.long_url, secret_key=secret_key)
        assert data['is_protected'] is True
        assert data['secret_key'] == secret_key

    def test_short_url_unshorten(self):
        data = shorten(self.long_url)
        udata = unshorten(data['short_code'])
        assert isinstance(udata, dict)
        assert udata['long_url'] == self.long_url
