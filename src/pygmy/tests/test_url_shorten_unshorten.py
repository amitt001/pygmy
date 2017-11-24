import os
import tempfile
from unittest import TestCase

from pygmy.core.initialize import initialize_test
from pygmy.app.link import shorten, unshorten
from pygmy.config import config


class URLShortenUnshortenTestCases(TestCase):
    """Tests to shorten-unshorten a long url"""

    DBPath = None

    def setUp(self):
        self.long_url = 'https://github.com'

    @classmethod
    def setUpClass(cls):
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_path = currdir + '/pygmy_test.cfg'
        db_path = tempfile.NamedTemporaryFile(suffix='.db').name
        cls.DBPath = db_path
        initialize_test(config_path, db_url=db_path)

    def test_config(self):
        assert config is not None
        assert config.db is not None
        assert self.DBPath is not None

    def test_long_url_shorten(self):
        data = shorten(self.long_url)
        assert isinstance(data, dict) is True
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
