from dataclasses import dataclass


@dataclass
class SearchParams:
    hledat: str = ""
    rub: str= "re"
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