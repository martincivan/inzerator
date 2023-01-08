import asyncio
from datetime import datetime, timedelta
import aiohttp

from inzerator.bazos.bazos import Bazos
from inzerator.bazos.bazos_api import BazosClient
from inzerator.bazos.rss import AuthorLoader, AuthorValidator
from inzerator.bazos.storage import ListingStorage, AuthorStorage
from inzerator.db.db import DB
from inzerator.rate_limiter import RateLimiter
from inzerator.users.searches import SearchStorage
from inzerator.search_scheduler import SearchRunner

BASE_URL = "https://www.bazos.sk/rss.php?"
URL_PARAMS = {
    "hledat": "",
    "rub": "re",
    "hlokalita": 83104,
    "humkreis": 25,
    "cenaod": "",
    "cenado": ""
}


def next_send():
    now = datetime.now()
    for i in (8, 12, 18):
        if now.hour < i:
            return now.replace(hour=i, minute=0, second=0, microsecond=0)
    return now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)


async def main():
    db = DB()
    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20, connect=10, sock_read=10, sock_connect=10)) as session:
        limiter = RateLimiter(session)
        listing_storage = ListingStorage(db.maker, db.engine)
        storage = AuthorStorage(db.maker)
        loader = Bazos(listing_storage,
                       AuthorLoader(author_storage=storage, session=limiter, author_validator=AuthorValidator(3)),
                       limiter, BazosClient(
                rate_limiter=limiter))
        search_storage = SearchStorage(db.maker)
        runner = SearchRunner(search_storage=search_storage, bazos=loader)
        await runner.run(datetime.now() - timedelta(seconds=5), datetime.now() - timedelta(hours=12))

if __name__ == "__main__":
    asyncio.run(main())
