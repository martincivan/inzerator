from typing import AsyncIterable

from inzerator.bazos.model import FeedItem
from inzerator.bazos.rss import Loader, SearchParams, AuthorLoader
from inzerator.bazos.storage import ListingStorage
from inzerator.rate_limiter import RateLimiter


class Bazos:
    BASE_URL = "https://www.bazos.sk/rss.php?"
    URL_PARAMS = {
        "hledat": "",
        "rub": "re",
        "hlokalita": 83104,
        "humkreis": 25,
        "cenaod": "",
        "cenado": ""
    }

    def __init__(self, listing_storage: ListingStorage, user_checker: AuthorLoader, session: RateLimiter):
        self.session = session
        self.listing_storage = listing_storage
        self.user_checker = user_checker

    async def load(self, search_params: SearchParams, user_id: int) -> AsyncIterable[FeedItem]:
        loader = Loader(self.BASE_URL, search_params=search_params, session=self.session)

        async for result in loader.__anext__():
            if await self.listing_storage.add(result, user_id) and await self.user_checker.load(result):
                yield result
