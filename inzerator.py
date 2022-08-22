import asyncio

import aiohttp

from inzerator.bazos.bazos import Bazos
from inzerator.bazos.model import SearchParams
from inzerator.bazos.rss import AuthorChecker
from inzerator.bazos.storage import ListingStorage, AuthorStorage
from inzerator.db.db import DB
from inzerator.rate_limiter import RateLimiter
from inzerator.users.inzerator_email import EmailSender
from inzerator.users.searches import SearchStorage

BASE_URL = "https://www.bazos.sk/rss.php?"
URL_PARAMS = {
    "hledat": "",
    "rub": "re",
    "hlokalita": 83104,
    "humkreis": 25,
    "cenaod": "",
    "cenado": ""
}


async def main():
    db = DB()
    sender = EmailSender()
    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20, connect=10, sock_read=10, sock_connect=10)) as session:
        limiter = RateLimiter(session)
        loader = Bazos(ListingStorage(db.maker), AuthorChecker(AuthorStorage(db.maker), 3, session=limiter), limiter)
        search_storage = SearchStorage(db.maker)
        email = None
        payload = ""
        for search in await search_storage.get_all():
            if email != search.user.email:
                if payload != "":
                    await sender.send_mail(email, payload)
                    payload = ""
                email = search.user.email
            async for result in loader.load(
                    SearchParams(search.query, search.category, search.subcategory, search.zip, search.diameter,
                                 search.price_from, search.price_to), search.user_id):
                payload += str(result)
        if payload != "":
            await sender.send_mail(email, payload)
        print("PAYLOAD: " + payload)

if __name__ == "__main__":
    asyncio.run(main())
