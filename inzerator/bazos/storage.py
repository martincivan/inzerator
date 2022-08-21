from typing import Optional

from inzerator.bazos.rss import FeedItem


class ListingStorage:

    def __init__(self):
        self.items = {}

    async def add(self, listing: FeedItem) -> bool:
        if listing.link in self.items:
            return False
        self.items[listing.link] = listing
        return True


class AuthorStorage:

    def __init__(self):
        self.items = {}

    async def add(self, user_id: str, valid: bool):
        self.items[user_id] = valid

    async def get(self, user_id: str) -> Optional[bool]:
        try:
            return self.items[user_id]
        except KeyError:
            return None

