import asyncio

from inzerator.db.db import DB
# noinspection PyUnresolvedReferences
from inzerator.users.users import User
# noinspection PyUnresolvedReferences
from inzerator.users.searches import Search
# noinspection PyUnresolvedReferences
from inzerator.bazos.storage import Author, Listing, Image
from inzerator.users.emails import Email


async def run():
    db = DB()
    await db.migrate()
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
