import json
import re

from bs4 import BeautifulSoup

from ..models import Listing
from ..parse import num
from .http import get

URL = (
    "https://www.immowelt.de/classified-search?distributionTypes=Rent"
    "&estateTypes=Apartment&locations=AD08DE8634&numberOfRoomsMin=3&priceMax=900"
)


def parse(html: str) -> list[Listing]:
    """Immowelt liefert Ergebnisse als JSON-LD bzw. in __NEXT_DATA__ / ld+json."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            for el in item.get("itemListElement", []) if isinstance(item, dict) else []:
                it = el.get("item", el)
                url = it.get("url") or ""
                if not url:
                    continue
                addr = it.get("address") or {}
                offers = it.get("offers") or {}
                out.append(Listing(
                    source="immowelt",
                    id=re.sub(r"\W+", "", url.rsplit("/", 1)[-1]) or url,
                    title=it.get("name", ""),
                    url=url,
                    rent_warm=num(str(offers.get("price", ""))) if offers else None,
                    rooms=num(str(it.get("numberOfRooms", ""))),
                    area_sqm=num(str((it.get("floorSize") or {}).get("value", ""))),
                    location=addr.get("addressLocality", "") if isinstance(addr, dict) else "",
                    description=it.get("description", ""),
                ))
    return out


def fetch(search: dict) -> list[Listing]:
    return parse(get(URL))
