from gcp import gcp_app
import sqlite3
from sqlalchemy import create_engine
import os
relative = "./"
dir_name = os.path.abspath(relative)
gcp_db_path = os.path.join(dir_name, 'gcp_init.db')


class Database:
    _db_engine = None

    def __init__(self):
        if self._db_engine is None:
            self._db_engine = self.create_db_engine()

    @staticmethod
    def create_db_engine():
        return create_engine(gcp_db_path, pool_size=5, pool_recycle=360, echo=True)
