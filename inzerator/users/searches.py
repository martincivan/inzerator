from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, select, TIMESTAMP, update
from sqlalchemy.orm import relationship, sessionmaker, joinedload

from inzerator.db import Base


class Search(Base):
    __tablename__ = 'searches'

    id = Column(Integer, primary_key=True)
    query = Column(String)
    category = Column(String)
    subcategory = Column(String)
    zip = Column(String)
    diameter = Column(Integer)
    price_from = Column(Integer)
    price_to = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    last_run_at = Column(TIMESTAMP)


class SearchStorage:

    def __init__(self, maker: sessionmaker):
        self.maker = maker

    async def get_all(self):
        async with self.maker() as session:
            result = await session.execute(select(Search).options(joinedload(Search.user)).order_by(Search.user_id))
            await session.commit()
            return result.scalars().all()

    async def get_run_before(self, run_before: datetime):
        async with self.maker() as session:
            result = session.execute(select(Search).where(Search.last_run_at < run_before).order_by(Search.last_run_at))
            await session.commit()
            result = await result
            return result.scalars().all()

    async def update_run(self, search: Search, run_at: datetime):
        async with self.maker() as session:
            stmt = (
                update(Search).
                where(Search.id == search.id).
                values(last_run_at=run_at)
            )
            await session.execute(stmt)
            await session.commit()
