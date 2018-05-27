import os
import tempfile
from unittest import TestCase

from pygmy.core.initialize import initialize_test
from pygmy.config import config


class URLClickStatsTest(TestCase):
    """Test for clickmeta i.e. click stats"""

    DBPath = None

    def setUp(self):
        self.long_url = 'https://example.com'

    @classmethod
    def setUpClass(cls):
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_path = currdir + '/pygmy_test.cfg'
        db_path = tempfile.NamedTemporaryFile(suffix='.db').name
        cls.DBPath = "sqlite:///{}".format(db_path)
        initialize_test(config_path, db_url=cls.DBPath)

    def test_config(self):
        assert config is not None
        assert config.db is not None
        assert self.DBPath is not None

    def test_clickmeta(self):
        from pygmy.app.link import shorten, unshorten, link_stats
        data = shorten(self.long_url)
        assert isinstance(data, dict) is True
        assert link_stats(data['short_code'] + 'abc+') is None
        stats = link_stats(data['short_code'] + '+')
        assert stats is not None
