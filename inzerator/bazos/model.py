from dataclasses import dataclass
from hashlib import md5
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

from aiohttp import ClientResponse


@dataclass
class SearchParams:
    hledat: str = ""
    rub: str = "re",
    cat: str = "152"
    hlokalita: int = 83104
    humkreis: int = 25
    cenaod: str = ""
    cenado: str = ""


@dataclass
class FeedItem:
    title: str
    price: str
    link: str
    summary: str
    image_link: str
    published: tuple[int]

    def __str__(self) -> str:
        return """
        
        %s - %s
        %s
        
        """ % (self.title, self.price, self.link)

    @property
    def ad_id(self) -> str:
        return PurePosixPath(unquote(urlparse(self.link).path)).parts[2]


class BazosImage:

    def __init__(self, url: str, data: ClientResponse) -> None:
        super().__init__()
        self.url = url
        self._data = data

    @property
    async def data(self):
        return await self._data.read()

    @property
    async def hash(self):
        data = await self._data.read()
        return md5(data).hexdigest()
