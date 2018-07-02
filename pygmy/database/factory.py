from pygmy.model import *
from pygmy.config import config
from pygmy.database.sqlite import SqliteDatabase
from pygmy.database.postgresql import PostgreSQLDatabase
from pygmy.database.mysql import MySQLDatabase
from pygmy.database.base import Model


class DatabaseFactory:

    @staticmethod
    def create():
        """Get db class from config.db.engine"""
        # TODO: make a utli.mapping
        if config.database['engine'] == 'sqlite3':
            database = SqliteDatabase()
        elif config.database['engine'] == 'postgresql':
            database = PostgreSQLDatabase()
        elif config.database['engine'] == 'mysql':
            database = MySQLDatabase()
        else:
            raise Exception(
                "Unsupported DB type. Supported types are "
                "postgresql/sqlite3 and mysql")
        database.initialize(config.debug)
        # Create all tables, if not already exists.
        Model.metadata.create_all(database.engine)
        # TODO DB: Run migrations
        return database
