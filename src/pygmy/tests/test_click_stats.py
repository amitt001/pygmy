import os
import tempfile
import unittest

from pygmy.app.link import shorten, link_stats
from pygmy.core.initialize import initialize_test
from pygmy.config import config


class URLClickStatsTest(unittest.TestCase):
    """Test for clickmeta i.e. click stats"""

    DBPath = None

    @classmethod
    def setup_class(cls):
        currdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = currdir + '/config/pygmy_test.cfg'
        db_path = tempfile.NamedTemporaryFile(suffix='.db').name
        cls.DBPath = "sqlite:///{}".format(db_path)
        initialize_test(config_path, db_url=cls.DBPath)
        cls.long_url = 'https://example.com'

    def test_config(self):
        assert config is not None
        assert config.db is not None
        assert self.DBPath is not None

    def test_clickmeta(self):
        data = shorten(self.long_url)
        self.assertTrue(isinstance(data, dict) is True)
        self.assertIsNone(link_stats(data['short_code'] + 'abc+'))
        stats = link_stats(data['short_code'] + '+')
        self.assertIsNotNone(stats)
