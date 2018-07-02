#!/usr/bin/env python3
"""Script when you just want to run Pygmy API."""

import sys
import tempfile

from pygmy.core.initialize import initialize, initialize_test


if __name__ == '__main__':

    # TODO: Use argparsep
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print('Running Pygmy API test server')

        config_path = 'pygmy/config/pygmy_test.cfg'
        db_file_path = tempfile.NamedTemporaryFile(suffix='.db').name
        db_path = "sqlite:///{}".format(db_file_path)

        initialize_test(config_path, db_url=db_path)
    else:
        print('Running Pygmy API server')
        initialize()

    from pygmy.rest.manage import run
    run()
