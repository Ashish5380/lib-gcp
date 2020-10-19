from sqlalchemy import Column, Integer, VARCHAR, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Mapping(Base):
    __tablename__ = "vm_image_mapping"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    vm_id = Column('vm_id', Integer)
    im_id = Column('im_id', Integer)
    status = Column('status',  SmallInteger, default=1)

    @staticmethod
    def create_table(engine):
        Base.metadata.create_all(engine)

    def __init__(self, data):
        self.vm_id = data['vm_id']
        self.im_id = data['im_id']
        self.status = data['status']

