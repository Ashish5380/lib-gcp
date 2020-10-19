from sqlalchemy import create_engine
import os
relative = "./"
dir_name = os.path.abspath(relative)
gcp_db_path = os.path.join(dir_name, 'gcp_init.db')
from gcp.models.vm_model import Vm
from gcp.models.image_model import Image


class Database:
    _db_engine = None

    def __init__(self):
        if self._db_engine is None:
            self._db_engine = self.create_db_engine()
        self.create_all_tables()

    @staticmethod
    def create_db_engine():
        return create_engine("sqlite:///"+gcp_db_path, pool_recycle=360, echo=True)

    def create_all_tables(self):
        Vm.create_table(self._db_engine)
        Image.create_table(self._db_engine)
