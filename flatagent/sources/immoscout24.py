import json
import re

from bs4 import BeautifulSoup

from ..models import Listing
from ..parse import num
from .http import get

URL = (
    "https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/unna-kreis/"
    "holzwickede/wohnung-mieten?numberofrooms=3.0-&price=-850.0&geocodes=1276010066"
)


def parse(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.select("a[href*='/expose/']"):
        m = re.search(r"/expose/(\d+)", a["href"])
        if not m:
            continue
        card = a.find_parent("article") or a
        out.append(Listing(
            source="immoscout24",
            id=m.group(1),
            title=a.get_text(" ", strip=True),
            url="https://www.immobilienscout24.de/expose/" + m.group(1),
            description=card.get_text(" ", strip=True),
            rent_warm=None,
            rooms=num(next(iter(re.findall(r"([\d,]+)\s*Zi", card.get_text(" "))), None)),
        ))
    return out


def fetch(search: dict) -> list[Listing]:
    # ImmoScout blockt Bots häufig (Captcha). Dann liefert get() einen Fehler
    # oder eine Seite ohne Treffer; beides wird in sources.fetch_all geloggt.
    return parse(get(URL))
