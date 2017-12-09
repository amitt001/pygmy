#!/usr/bin/env python3
"""Script when you just want to run Pygmy API."""

from pygmy.core.initialize import initialize
initialize()
from pygmy.rest.manage import run


run()
