import asyncio
from datetime import datetime

from inzerator.users.searches import SearchStorage
from inzerator.bazos.model import SearchParams
from inzerator.bazos.bazos import Bazos


class SearchRunner:

    def __init__(self, search_storage: SearchStorage, bazos: Bazos) -> None:
        super().__init__()
        self.bazos = bazos
        self.search_storage = search_storage

    async def run(self, last_search_before: datetime, last_open_before: datetime):
        res = [self.process_search(search=search) for search in
               await self.search_storage.get_run_before(last_search_before)]
        await asyncio.gather(*res)
        await self.bazos.process_open(last_open_before)

    async def process_search(self, search):
        params = SearchParams(search.query, search.category, search.subcategory, search.zip, search.diameter,
                              search.price_from, search.price_to)
        async for result in self.bazos.process_feed(params, search.user_id):
            pass
        await self.search_storage.update_run(search, run_at=datetime.now())
