from pygmy.model import *
from pygmy.config import config
from pygmy.database.sqlite import SqliteDatabase
from pygmy.database.postgresql import PostgreSQLDatabase
from pygmy.database.base import Model


class DatabaseFactory:

    @staticmethod
    def create():
        """Get db class from config.db.engine"""
        # TODO: make a utli.mapping
        if config.database['engine'] == 'sqlite3':
            database = SqliteDatabase()
        if config.database['engine'] == 'postgresql':
            database = PostgreSQLDatabase()
        database.initialize()
        # Create all tables, if not already exists.
        Model.metadata.create_all(database.engine)
        # TODO DB: Run migrations
        return database
