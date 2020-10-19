from gcp import gcp_app
import sqlite3
from sqlalchemy import create_engine


class Database:
    _db_engine = None

    def __init__(self):
        if self._db_engine is None:
            self._db_engine = self.create_db_engine()

    @staticmethod
    def create_db_engine():
        return create_engine('sqlite:///:memory:', pool_size=5, pool_recycle=360, echo=True)
