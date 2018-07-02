#!/usr/bin/env python3

import pygmy
import traceback

from pygmy.core.initialize import initialize
from pygmy.config import config
from pygmy.app.link import shorten, unshorten, link_stats
from pygmy.model import *

initialize()

banner = """
        ************************************
       * Pygmy: Open Source Link Shortner *
      ************************************
      """
db = config.db.store
pygmy_context = dict(pygmy=pygmy, config=config,
                     Link=Link, LinkManager=LinkManager,
                     User=User, UserManager=UserManager,
                     shorten=shorten, unshorten=unshorten,
                     link_stats=link_stats, db=db)


def ipython_shell(namespace=None, banner=None, debug=False):
    """Try to run IPython shell."""
    try:
        import IPython
    except ImportError:
        if debug:
            traceback.print_exc()
        print("IPython not available. Running default shell...")
        return
    # First try newer(IPython >=1.0) top `IPython` level import
    if hasattr(IPython, 'terminal'):
        from IPython.terminal.embed import InteractiveShellEmbed
        kwargs = dict(user_ns=namespace)
    else:
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        kwargs = dict(user_ns=namespace)
    if banner:
        kwargs = dict(banner1=banner)
    return InteractiveShellEmbed(**kwargs)


def python_shell(namespace=None, banner=None, debug=False):
    """Start a vanilla Python REPL shell."""
    import code
    from functools import partial
    try:
        import readline, rlcompleter    # NOQA
    except ImportError:
        if debug:
            traceback.print_exc()
    else:
        readline.parse_and_bind('tab: complete')
    # Add global, local and custom namespaces to current shell
    default_ns = globals().copy()
    default_ns.update(locals())
    if namespace:
        default_ns.update(namespace)
    # Configure kwargs to pass banner
    kwargs = dict()
    if banner:
        kwargs = dict(banner=banner)
    shell = code.InteractiveConsole(default_ns)
    return partial(shell.interact, **kwargs)


def console(use_ipython=True, namespace=None, banner=None, debug=False):
    namespace = {} if namespace is None else namespace
    namespace.update(pygmy_context)

    # Setup the shell
    shell = None
    if use_ipython:
        shell = ipython_shell(namespace, banner, debug)
    if not use_ipython or shell is None:
        shell = python_shell(namespace, banner, debug)
    shell()

# In future setup.py will make pygmy a command and typing pygmy console
# will start the shell
console()
