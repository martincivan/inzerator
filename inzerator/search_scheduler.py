import datetime

from inzerator.users.searches import SearchStorage
from inzerator.bazos.model import SearchParams
from inzerator.bazos.bazos import Bazos


class SearchRunner:

    def __init__(self, search_storage: SearchStorage, loader: Bazos) -> None:
        super().__init__()
        self.loader = loader
        self.search_storage = search_storage

    async def run(self, last_run_before: datetime.datetime):
        for search in await self.search_storage.get_run_before(last_run_before):
            params = SearchParams(search.query, search.category, search.subcategory, search.zip, search.diameter,
                                  search.price_from, search.price_to)
            async for result in self.loader.load(params, search.user_id):
                pass
            await self.search_storage.update_run(search, run_at=datetime.datetime.now())
