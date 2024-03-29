import asyncio
import dataclasses
import re
import urllib.parse
from typing import Optional, AsyncIterable
from bs4 import BeautifulSoup
from functools import reduce
import feedparser
import logging

from inzerator.bazos.model import SearchParams, FeedItem
from inzerator.bazos.bazos_api import ApiData
from inzerator.bazos.storage import AuthorStorage
from inzerator.rate_limiter import RateLimiter


class RSSLoader:

    def __init__(self, baseurl: str, search_params: SearchParams, session: RateLimiter):
        self.session = session
        self.baseUrl = baseurl
        self.search_params = search_params
        self.data = None

    def __aiter__(self):
        return self

    async def __anext__(self) -> AsyncIterable[FeedItem]:
        if not self.data:
            while not await self.load():
                logging.warning("rate limited, sleeping for 10mins")
                print("rate limited, sleeping for 10mins")
                await asyncio.sleep(600)
        for i in self.data:
            yield i

    async def load(self) -> bool:
        search_params = {k: v for k, v in self.search_params.__dict__.items() if v is not None}
        async with await self.session.get(self.baseUrl + urllib.parse.urlencode(search_params)) as html:
            result = await html.text()
            if html.status != 200:
                return False
            self.data = []
            rss = feedparser.parse(result)
            for record in rss.entries:
                title, price = record.title.rsplit(':', 1)
                try:
                    image_link = record.summary.split('"', 4)[3]
                except IndexError:
                    image_link = None
                self.data.append(
                    FeedItem(title=title, price=price, link=record.link, summary=record.summary, image_link=image_link,
                             published=record.published_parsed))
        return True


@dataclasses.dataclass
class AuthorData:
    name: str
    listing_count: int
    listing_urls: list[str]
    url: str


class AuthorValidator:

    def __init__(self, real_listing_threshold: int):
        self.real_listing_threshold = real_listing_threshold

    def validate(self, data: AuthorData) -> bool:
        return self.validate_listings(data.listing_urls) and self.validate_name(data.name)

    def validate_listings(self, urls: list[str]) -> bool:
        count = reduce(lambda x, y: x + 1, filter(lambda u: u.startswith("https://reality.bazos.sk/inzerat/"), urls), 0)
        return count < self.real_listing_threshold

    def validate_name(self, name: str) -> bool:
        pattern = '.*[A-Z]{3}.*'
        return re.search(pattern, name) is None and not any(sub in name for sub in ["S.R.O", "s.r.o", "real", "Real", "REAL"])


class AuthorLoader:

    def __init__(self, author_storage: AuthorStorage, session: RateLimiter, author_validator: AuthorValidator):
        self.session = session
        self.author_storage = author_storage
        self.user_listing_number = "Všetky inzeráty užívateľa \((\d+)\)\:"
        self.author_validator = author_validator

    async def check(self, data: ApiData) -> Optional[bool]:
        author_valid = await self.author_storage.get(email_id=data.email_id, phone_id=data.phone_id)
        if author_valid is None:
            author_valid = await self._validate_author(
                "https://www.bazos.sk/hodnotenie.php?idmail=%s&idphone=%s" % (data.email_id, data.phone_id),
                phone_id=data.phone_id,
                email_id=data.email_id, name=data.name)
        return author_valid

    async def _validate_author(self, author_url: str, phone_id: str, email_id: str, name: str) -> Optional[bool]:
        async with await self.session.get(author_url) as html:
            listing_text = await html.text()
            parser = AuthorDataParser()
            data = parser.parse(listing_text, author_url, name)
            result = self.author_validator.validate(data)
            if not result:
                await self.author_storage.add(phone_id=phone_id, email_id=email_id, valid=result)
            return result


def _parse_name(html: str, url: str) -> str:
    regex = "Užívateľ (.+):"
    result = re.search(regex, html)
    if result is None or not len(result.groups()):
        logging.warning("Author name pattern not matched.", {"link": url})
        return ""
    return result.groups()[0]


def _parse_listing_count(html: str, url: str) -> int:
    regex = "Všetky inzeráty užívateľa \((\d+)\)\:"
    result = re.search(regex, html)
    if result is None or not len(result.groups()):
        logging.warning("Listing count pattern not matched.", {"link": url})
        return 0
    return int(result.groups()[0])


def _parse_listings(html: str, url: str) -> list[str]:
    parser = BeautifulSoup(html, features="lxml")
    parts = parser.find_all(class_="inzeratynadpis")
    if not len(parts):
        logging.warning("List of listing not matched", {"link": url})
        return []
    parts.pop(0)
    return list(map(lambda e: e.next.get("href"), parts))


class AuthorDataParser:

    def parse(self, html: str, url: str, name: Optional[str]) -> AuthorData:
        name = name or _parse_name(html, url)
        listing_count = _parse_listing_count(html, url)
        listing_urls = _parse_listings(html, url)

        return AuthorData(name, listing_count, listing_urls, url)
