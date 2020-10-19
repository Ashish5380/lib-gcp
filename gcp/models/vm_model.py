from sqlalchemy import Column, Integer, VARCHAR, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vm(Base):
    __tablename__ = "vm"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    vm_name = Column('vm_name', VARCHAR)
    zone = Column('zone', VARCHAR)
    project = Column('project', VARCHAR)
    is_stopped = Column('is_stopped', SmallInteger, default=0)
    status = Column('status', SmallInteger, default=1)

    @staticmethod
    def create_table(engine):
        Base.metadata.create_all(engine)

    def __init__(self, data):
        self.vm_name = data['vm_name']
        self.zone = data['zone']
        self.project = data['project']
        self.status = data['status']
        self.id_stopped = data['is_stopped']

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(cls).filter_by(vm_name=name).filter_by(status=1).all()

    @classmethod
    def find_by_id(cls, session, vm_id):
        return session.query(cls).filter_by(id=vm_id).all()