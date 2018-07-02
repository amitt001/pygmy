#!/usr/bin/env python3
from pygmy.core.initialize import initialize
initialize()
from pygmy.rest.manage import app

if __name__ == '__main__':
    app.run()
