
from functools import wraps
from pygmy.config import config
from sqlalchemy.exc import SQLAlchemyError


def dbconnection(func):

    @wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            if len(args) > 0:
                return func(args[0], config.db.store, *args[1:], **kwargs)
            else:
                return func(config.db.store, **kwargs)
        except SQLAlchemyError:
            config.db.store.rollback()
            raise
    return _wrapped
