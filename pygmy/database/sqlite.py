import os

from urllib.parse import urlparse
from pygmy.database.base import BaseDatabase


class SqliteDatabase(BaseDatabase):

    def _prepare(self, url):
        """Touch sqlite file."""
        urlp = urlparse(url)
        path = os.path.normpath(urlp.path)
        if not os.path.exists(path):
            with open(path, 'w') as _:
                pass
