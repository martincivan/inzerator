import re
import urllib.parse
from typing import Optional, AsyncIterable

import feedparser
import logging

from inzerator.bazos.model import SearchParams, FeedItem
from inzerator.bazos.storage import UserStorage
from inzerator.rate_limiter import RateLimiter


class Loader:

    def __init__(self, baseurl: str, search_params: SearchParams, session: RateLimiter):
        self.session = session
        self.baseUrl = baseurl
        self.search_params = search_params
        self.data = None

    def __aiter__(self):
        return self

    async def __anext__(self) -> AsyncIterable[FeedItem]:
        if not self.data:
            await self.load()
        for i in self.data:
            yield i

    async def load(self):
        async with await self.session.get(self.baseUrl + urllib.parse.urlencode(self.search_params.__dict__)) as html:
            result = await html.text()
            self.data = []
            rss = feedparser.parse(result)
            for record in rss.entries:
                title, price = record.title.rsplit(' - ', 1)
                try:
                    image_link = record.summary.split('"', 4)[3]
                except IndexError:
                    image_link = None
                self.data.append(
                    FeedItem(title=title, price=price, link=record.link, summary=record.summary, image_link=image_link,
                             published=record.published_parsed))


class UserChecker:

    def __init__(self, user_storage: UserStorage, listing_threshold: int, session: RateLimiter):
        self.session = session
        self.listing_threshold = listing_threshold
        self.user_storage = user_storage
        self.user_pattern = "\"(https://www.bazos.sk/hodnotenie.php\\?[^\s]*)\""
        self.user_listing_number = "Všetky inzeráty užívateľa \((\d+)\)\:"

    async def load(self, feed_item: FeedItem) -> Optional[bool]:
        async with await self.session.get(feed_item.link) as html:
            listing_text = await html.text()
            result = re.search(self.user_pattern, listing_text)
            if result is None or not len(result.groups()):
                logging.warning("User pattern not matched.",
                                {"listing_link": feed_item.link, "listing_text": listing_text})
                return
            if await self.user_storage.get(result.groups()[0]):
                return False
            return await self._load_user(self.session, result.groups()[0])

    async def _load_user(self, session, user_url: str) -> Optional[bool]:
        async with await self.session.get(user_url) as html:
            listing_text = await html.text()
            count = re.search(self.user_listing_number, listing_text)
            if count is None or not len(count.groups()):
                logging.warning("User listing count pattern not matched.",
                                {"user_link": user_url, "user_text": listing_text})
                return
            result = int(count.groups()[0]) <= self.listing_threshold
            await self.user_storage.add(user_url, result)
            return result
