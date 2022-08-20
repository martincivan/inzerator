import asyncio

import aiohttp

from inzerator.bazos.bazos import Bazos
from inzerator.bazos.rss import Loader, SearchParams, UserChecker
from inzerator.bazos.storage import ListingStorage, UserStorage
from inzerator.rate_limiter import RateLimiter

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
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20, connect=10, sock_read=10, sock_connect=10)) as session:
        limiter = RateLimiter(session)
        loader = Bazos(ListingStorage(), UserChecker(UserStorage(), 3, session=limiter), limiter)
        async for result in loader.load():
            print(result.title)
            print(result.link)

    # with open("test2.html", 'r') as file:
    #     text = file.read()
    #     result = re.search("Všetky inzeráty užívateľa \((\d+)\)\:", text)
    #     print(result)

if __name__ == "__main__":
    asyncio.run(main())
