import datetime
from typing import List

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Text, select, delete
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from sqlalchemy.sql import text

from inzerator.db import Base


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    send_after = Column(TIMESTAMP)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User")


class EmailStorage:

    def __init__(self, maker: sessionmaker, engine: Engine):
        self.engine = engine
        self.maker = maker

    async def add(self, user_id: int, body: str, send_after: datetime.datetime):
        async with self.engine.connect() as conn:
            conn.begin()
            statement = text("""INSERT INTO emails(text, send_after, user_id) VALUES(:text, :send, :user_id) ON
            CONFLICT(user_id) DO UPDATE SET text = emails.text || :text""")

            await conn.execute(statement, {"text": body, "send": send_after, "user_id": user_id})
            await conn.commit()

    async def get_to_send(self, send_after: datetime.datetime) -> List[Email]:
        async with self.maker() as session:
            result = await session.execute(
                select(Email).options(joinedload(Email.user)).filter(Email.send_after <= send_after))
            await session.commit()
            return result.scalars().all()

    async def remove(self, email_id: int):
        async with self.maker() as session:
            await session.execute(
                delete(Email).where(Email.id == email_id))
            await session.commit()
