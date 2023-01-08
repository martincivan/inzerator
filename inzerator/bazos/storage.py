import logging
from datetime import datetime
from dateutil import parser
from typing import Optional, AsyncIterable, Any

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, Text, LargeBinary, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text, select

from inzerator.bazos.bazos_api import ApiData
from inzerator.bazos.model import BazosImage
from inzerator.db import Base
from inzerator.users.users import User

from dataclasses import asdict


class Listing(Base):
    __tablename__ = 'listings'

    id = Column(String, primary_key=True)
    url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User.__name__)
    phone_id = Column(String)
    email_id = Column(String)
    last_processed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)
    removed_at = Column(TIMESTAMP)
    status = Column(String)
    title = Column(String)
    description = Column(Text)
    currency = Column(String)
    price = Column(Integer)
    zip_code = Column(String)
    section_id = Column(String)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ListingStorage:

    def __init__(self, maker: sessionmaker, engine: Engine):
        self.engine = engine
        self.maker = maker

    async def add(self, listing: ApiData, images: AsyncIterable[BazosImage], user_id: int) -> bool:
        async with self.maker() as session:
            try:
                async with session.begin():
                    params = {**asdict(listing), "created_at": parser.parse(listing.created_at).replace(tzinfo=None),
                              "user_id": user_id,
                              "last_processed_at": datetime.now(), "price": int(listing.price)}
                    del (params["images"])
                    del (params["name"])
                    session.add(Listing(**params))
                    await session.commit()
                async with session.begin():
                    async for image in images:
                        data = await image.data
                        image_hash = await image.hash
                        session.add(Image(listing_id=listing.id, url=image.url, hash=image_hash, file=data))
                    await session.commit()
                return True
            except IntegrityError:
                logging.exception("Inserting Listing failed.")
                await session.rollback()
                return False

    async def get(self, id: str) -> Optional[Listing]:
        async with self.maker() as session:
            async with session.begin():
                query = select(Listing).where(Listing.id == id)
                results = await session.execute(query)
                try:
                    (result,) = results.one()
                except NoResultFound:
                    return None
                return result

    async def remove_older(self, than: datetime):
        async with self.engine.connect() as conn:
            conn.begin()
            statement = text("""DELETE FROM listings WHERE processed_at < :than""")
            await conn.execute(statement, {"than": than})
            await conn.commit()

    async def get_open_before(self, last_open_before) -> AsyncIterable[Listing]:
        async with self.maker() as session:
            async with session.begin():
                query = select(Listing).where(Listing.last_processed_at < last_open_before).where(
                    Listing.removed_at.is_(None))
                results = await session.execute(query)
                for row in results:
                    yield row[0]

    async def save_removed_processed(self, listing: Listing):
        async with self.maker() as session:
            stmt = (
                update(Listing).
                where(Listing.id == listing.id).
                values(last_processed_at=listing.last_processed_at).
                values(removed_at=listing.removed_at)
            )
            await session.execute(stmt)
            await session.commit()


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(String, ForeignKey("listings.id"), primary_key=True)
    url = Column(String)
    hash = Column(String)
    file = Column(LargeBinary)


class AuthorStorage:

    def __init__(self, maker: sessionmaker):
        self.maker = maker

    async def add(self, phone_id: str, email_id: str, valid: bool):
        async with self.maker() as session:
            try:
                async with session.begin():
                    session.add(Author(email_id=email_id, phone_id=phone_id, valid=valid, processed_at=datetime.now()))
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def get(self, phone_id: str, email_id: str) -> Optional[bool]:
        async with self.maker() as session:
            result = await session.get(Author, (phone_id, email_id))
            await session.commit()
            return result.valid if result else None


class Author(Base):
    __tablename__ = 'authors'

    email_id = Column(String, primary_key=True)
    phone_id = Column(String, primary_key=True)
    valid = Column(Boolean)
    processed_at = Column(TIMESTAMP)
