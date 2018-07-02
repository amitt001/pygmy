
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from pygmy.config import config


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


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow)
def __utcnow_default(element, compiler, **kw):
    return 'CURRENT_TIMESTAMP'


# @compiles(utcnow, 'mysql')
# def __utcnow_mysql(element, compiler, **kw):
#     return 'UTC_TIMESTAMP()'


@compiles(utcnow, 'postgresql')
def __utcnow_pg(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
