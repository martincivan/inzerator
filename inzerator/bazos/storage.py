from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, sessionmaker

from inzerator.bazos.model import FeedItem
from inzerator.db import Base
from inzerator.users.users import User


class ListingStorage:

    def __init__(self, maker: sessionmaker, engine: Engine):
        self.engine = engine
        self.maker = maker

    async def add(self, listing: FeedItem, user_id: int) -> bool:
        async with self.maker() as session:
            try:
                async with session.begin():
                    session.add(Listing(id=listing.link, user_id=user_id, processed_at=datetime.now()))
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def remove_older(self, than: DateTime):
        async with self.engine.connect() as conn:
            conn.begin()
            statement = text("""DELETE FROM listings WHERE processed_at < :than""")
            await conn.execute(statement, {"than": than})
            await conn.commit()


class Listing(Base):
    __tablename__ = 'listings'

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship(User.__name__)
    processed_at = Column(TIMESTAMP)


class AuthorStorage:

    def __init__(self, maker: sessionmaker):
        self.maker = maker

    async def add(self, user_id: str, valid: bool):
        async with self.maker() as session:
            try:
                async with session.begin():
                    session.add(Author(id=user_id, valid=valid, processed_at=datetime.now()))
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def get(self, user_id: str) -> Optional[bool]:
        async with self.maker() as session:
            result = await session.get(Author, user_id)
            await session.commit()
            return result.valid if result else None


class Author(Base):
    __tablename__ = 'authors'

    id = Column(String, primary_key=True)
    valid = Column(Boolean)
    processed_at = Column(TIMESTAMP)
