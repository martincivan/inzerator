import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from inzerator.db import Base


class DB:

    def __init__(self):
        # "postgresql+asyncpg://scott:tiger@localhost/test",
        db_host = os.environ.get("DATABASE_URL")
        if db_host and db_host.startswith("postgres://"):
            db_host = db_host.replace("postgres://", "postgresql+asyncpg://", 1)
        self.engine = create_async_engine(
            db_host,
            # echo=True,
        )
        self._maker = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def maker(self) -> sessionmaker:
        return self._maker

    async def disconnect(self):
        await self.engine.dispose()

    async def migrate(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            conn.begin()
            statement = text("""INSERT INTO users (name, email) VALUES ('A', 'a@a.a')""")
            await conn.execute(statement)
            statement = text(
                """INSERT INTO searches (category, subcategory, zip, diameter, price_from, price_to, user_id, last_run_at) VALUES ('re', '152', '82104', 25, 10000, 10000000, 1, '2023-01-07 20:12:50.079541'::TIMESTAMP)""")
            await conn.execute(statement)
            await conn.commit()
