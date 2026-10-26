from bs4 import BeautifulSoup

from ..models import Listing
from ..parse import num
from .http import get

BASE = "https://www.kleinanzeigen.de"
# c203 = Mietwohnungen; PLZ-Ort/Radius über die Suchseite
URL = BASE + "/s-wohnung-mieten/holzwickede/anzeige:angebote/c203l1980r6"


def parse(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for ad in soup.select("article.aditem"):
        link = ad.select_one("a[href*='/s-anzeige/']")
        if not link:
            continue
        title = link.get_text(" ", strip=True)
        href = link["href"]
        text = lambda sel: (ad.select_one(sel).get_text(" ", strip=True) if ad.select_one(sel) else "")
        tags = " ".join(t.get_text(" ", strip=True) for t in ad.select(".simpletag"))
        rooms = num(next((t.get_text() for t in ad.select(".simpletag") if "Zimmer" in t.get_text()), None))
        area = num(next((t.get_text() for t in ad.select(".simpletag") if "m²" in t.get_text()), None))
        out.append(Listing(
            source="kleinanzeigen",
            id=ad.get("data-adid") or href.rsplit("/", 1)[-1],
            title=title,
            url=BASE + href if href.startswith("/") else href,
            rent_cold=num(text(".aditem-main--middle--price-shipping--price")),
            rooms=rooms,
            area_sqm=area,
            location=text(".aditem-main--top--left"),
            description=text(".aditem-main--middle--description") + " " + tags,
        ))
    return out


def fetch(search: dict) -> list[Listing]:
    return parse(get(URL))
