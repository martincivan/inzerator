import asyncio
from datetime import datetime, timedelta

from aiohttp import ClientSession
from typing import AsyncIterable, Optional

from inzerator.bazos.bazos_api import BazosClient
from inzerator.bazos.model import FeedItem, BazosImage
from inzerator.bazos.rss import RSSLoader, SearchParams, AuthorLoader
from inzerator.bazos.storage import ListingStorage, Listing
from inzerator.rate_limiter import RateLimiter


class FreshValidator:

    def __call__(self, listing: Optional[Listing]):
        return listing and listing.last_processed_at > datetime.now() + timedelta(days=-1)


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
        self.fresh = FreshValidator()

    async def load_images(self, links: list[str]) -> AsyncIterable[BazosImage]:
        async with ClientSession() as client:
            for link in links:
                yield BazosImage(link, await client.get(link))

    async def process_feed(self, search_params: SearchParams, user_id: int) -> AsyncIterable[FeedItem]:
        loader = RSSLoader(self.BASE_URL, search_params=search_params, session=self.session)

        async for feed_item in loader.__anext__():
            existing = await self.listing_storage.get(feed_item.ad_id)
            if self.fresh(existing):
                yield feed_item
                continue
            data = await self.api.get_data(feed_item.ad_id)
            images = self.load_images(data.images)
            if await self.listing_storage.add(data, images, user_id) and await self.user_checker.check(data):
                yield feed_item

    async def process_open(self, last_open_before: datetime):
        res = [self.process_open_listing(listing=listing) async for listing in
               self.listing_storage.get_open_before(last_open_before=last_open_before)]
        await asyncio.gather(*res)

    async def process_open_listing(self, listing):
        data = await self.api.get_data(listing.id)
        listing.last_processed_at = datetime.now()
        if not data:
            listing.removed_at = datetime.now()
        await self.listing_storage.save_removed_processed(listing)
