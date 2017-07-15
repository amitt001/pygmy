
from functools import wraps
from pygmy.config import config


def dbconnection(func):

    @wraps(func)
    def _wrapped(*args, **kwargs):
        if len(args) > 0:
            return func(args[0], config.db.store, **kwargs)
        else:
            return func(config.db.store, **kwargs)
    return _wrapped
