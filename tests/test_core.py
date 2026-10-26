from flatagent import filters, mailer
from flatagent.config import load_config
from flatagent.models import Listing
from flatagent.parse import num
from flatagent.sources import kleinanzeigen
from flatagent.storage import SeenStore

S = load_config("config.yaml")["search"]


def L(**kw):
    base = dict(source="t", id="1", title="3 Zimmer Wohnung", url="http://x", location="Holzwickede")
    return Listing(**{**base, **kw})


def test_num():
    assert num("1.234,50 €") == 1234.5
    assert num("3,5 Zi.") == 3.5
    assert num(None) is None


def test_filter_rent_rooms_place():
    assert filters.matches(L(rooms=3, rent_warm=800), S)
    assert not filters.matches(L(rooms=3, rent_warm=900), S)
    assert not filters.matches(L(rooms=2, rent_warm=700), S)
    assert not filters.matches(L(rooms=3, rent_warm=700, location="Hamburg"), S)
    assert not filters.matches(L(rooms=3, rent_warm=700, title="Wohnungstausch 3 Zi"), S)


def test_filter_unknown_values_pass():
    assert filters.matches(L(), S)


def test_cold_rent_estimate():
    assert not filters.matches(L(rooms=3, rent_cold=800, area_sqm=70), S)
    assert filters.matches(L(rooms=3, rent_cold=550, area_sqm=70), S)


def test_store(tmp_path):
    p = tmp_path / "seen.json"
    s = SeenStore(p)
    assert s.is_new("a")
    s.add("a"); s.save()
    assert not SeenStore(p).is_new("a")


def test_kleinanzeigen_parse():
    html = """<article class="aditem" data-adid="42"><a href="/s-anzeige/foo/42-203-1980">Schöne 3 Zi</a>
    <div class="aditem-main--top--left">59439 Holzwickede</div>
    <p class="aditem-main--middle--price-shipping--price">700 €</p>
    <span class="simpletag">3 Zimmer</span><span class="simpletag">70 m²</span></article>"""
    [l] = kleinanzeigen.parse(html)
    assert (l.id, l.rent_cold, l.rooms, l.area_sqm) == ("42", 700.0, 3.0, 70.0)
    assert l.url.startswith("https://www.kleinanzeigen.de/s-anzeige/")


def test_mail_render():
    subj, body = mailer.render([(L(rent_warm=800, rooms=3), "Hallo")])
    assert "1 neue" in subj and "Hallo" in body and "http://x" in body
