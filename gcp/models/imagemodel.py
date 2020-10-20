from sqlalchemy import Column, Integer, VARCHAR, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ImageModel(Base):
    __tablename__ = "images"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    image_name = Column('image_name', VARCHAR)
    family_name = Column('family_name', VARCHAR)
    status = Column('status', SmallInteger, default=1)
    is_dirty_resource = Column('is_dirty_resource', SmallInteger, default=0)

    @staticmethod
    def create_table(engine):
        Base.metadata.create_all(engine)

    def __init__(self, data):
        self.image_name = data['image_name']
        self.status = data['status']
        self.is_dirty_resource = data['is_dirty_resource']
        self.family_name = data['family_name']

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(cls).filter_by(image_name=name).filter_by(status=1).first()


