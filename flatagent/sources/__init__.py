import logging

from . import immoscout24, immowelt, kleinanzeigen

log = logging.getLogger(__name__)

ALL = {
    "kleinanzeigen": kleinanzeigen,
    "immowelt": immowelt,
    "immoscout24": immoscout24,
}


def fetch_all(config: dict) -> list:
    listings = []
    for name, module in ALL.items():
        if not config["sources"].get(name):
            continue
        try:
            found = module.fetch(config["search"])
            log.info("%s: %d Angebote", name, len(found))
            listings += found
        except Exception as e:  # eine kaputte Quelle darf die anderen nicht stoppen
            log.warning("%s fehlgeschlagen: %s", name, e)
    return listings
