from sqlalchemy import Column, Integer, String

from inzerator.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    # def __repr__(self):
    #     return "<User(name='%s', email='%s')>" % (self.name, self.email)
