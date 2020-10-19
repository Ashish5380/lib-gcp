from sqlalchemy import Column, Integer, VARCHAR, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Image(Base):
    __tablename__ = "images"


