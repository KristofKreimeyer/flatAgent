import argparse
import logging

from . import letter, mailer
from .config import load_config
from .filters import matches
from .sources import fetch_all
from .storage import SeenStore

log = logging.getLogger("flatagent")


def run(config_path: str, dry_run: bool) -> int:
    config = load_config(config_path)
    store = SeenStore()

    new = [
        l for l in fetch_all(config)
        if store.is_new(l.key) and matches(l, config["search"])
    ]
    log.info("%d neue passende Angebote", len(new))
    if not new:
        return 0

    items = []
    for l in new:
        try:
            items.append((l, letter.write_letter(l, config)))
        except Exception as e:
            log.warning("Anschreiben für %s fehlgeschlagen: %s", l.url, e)
            items.append((l, "(Anschreiben konnte nicht erzeugt werden)"))

    subject, body = mailer.render(items)
    if dry_run:
        print(subject, "\n", body)
        return len(new)

    mailer.send(config["mail"]["to"], subject, body)
    for l, _ in items:
        store.add(l.key)
    store.save()
    return len(new)


def cli() -> None:
    ap = argparse.ArgumentParser(prog="flatagent")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--dry-run", action="store_true", help="Mail nur ausgeben, nichts senden/speichern")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run(args.config, args.dry_run)


if __name__ == "__main__":
    cli()
