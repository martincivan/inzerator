from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from random import randint, choice

from inzerator.rate_limiter import RateLimiter
from typing import Optional, Any

URL = 'https://www.bazos.sk/api/v1/ad-detail-2.php?ad_id='
headers = {
    'user-agent': 'bazos/2.12.1 (cz.ackee.bazos; build:3582; android' + choice(["11", "10", "12"]) + '; model:Samsung '
                                                                                                     'Galaxy S20) '
                                                                                                     'okhttp/4.8.1',
    'x-deviceid': str(randint(10000000, 99999999))
}


@dataclass_json
@dataclass
class ApiData:
    id: str
    created_at: str = field(metadata=config(field_name="from"))
    status: str
    title: str
    description: str
    currency: str
    price: str
    zip_code: str
    url: str
    images: list[str]
    name: str
    phone_id: Optional[str] = None
    email_id: Optional[str] = None


class BazosClient:

    def __init__(self, rate_limiter: RateLimiter) -> None:
        super().__init__()
        self.session = rate_limiter

    async def get_data(self, ad_id: int) -> Any | None:
        async with await self.session.get(URL + str(ad_id), headers=headers) as data:
            json = await data.read()
            try:
                return ApiData.from_json(json)
            except KeyError:
                return None
