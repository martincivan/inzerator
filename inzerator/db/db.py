import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from inzerator.db import Base


class DB:

    def __init__(self):
        # "postgresql+asyncpg://scott:tiger@localhost/test",
        self._engine = create_async_engine(
            os.environ.get("DATABASE_URL"),
            # echo=True,
        )
        self._maker = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def maker(self) -> sessionmaker:
        return self._maker

    async def disconnect(self):
        await self._engine.dispose()

    async def migrate(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
