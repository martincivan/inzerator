from aiohttp import ClientSession
from typing import AsyncIterable

from inzerator.bazos.bazos_api import BazosClient
from inzerator.bazos.model import FeedItem, BazosImage
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

    def __init__(self, listing_storage: ListingStorage, user_checker: AuthorLoader, session: RateLimiter,
                 api: BazosClient):
        self.api = api
        self.session = session
        self.listing_storage = listing_storage
        self.user_checker = user_checker
        self.client = ClientSession()

    async def load_images(self, links: list[str]) -> AsyncIterable[BazosImage]:
        for link in links:
            yield BazosImage(link, await self.client.get(link))

    async def load(self, search_params: SearchParams, user_id: int) -> AsyncIterable[FeedItem]:
        loader = Loader(self.BASE_URL, search_params=search_params, session=self.session)

        async for result in loader.__anext__():
            data = await self.api.get_data(result.ad_id)
            images = self.load_images(data.images)
            if await self.listing_storage.add(data, images, user_id) and await self.user_checker.load(data, result):
                yield result
