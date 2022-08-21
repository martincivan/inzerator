from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship, sessionmaker, joinedload

from inzerator.db import Base


class Search(Base):
    __tablename__ = 'searches'

    id = Column(Integer, primary_key=True)
    query = Column(String)
    category = Column(String)
    subcategory = Column(String)
    zip = Column(Integer)
    diameter = Column(Integer)
    price_from = Column(Integer)
    price_to = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")


class SearchStorage:

    def __init__(self, maker: sessionmaker):
        self.maker = maker

    async def get_all(self):
        async with self.maker() as session:
            result = await session.execute(select(Search).options(joinedload(Search.user)).order_by(Search.user_id))
            await session.commit()
            return result.scalars().all()
