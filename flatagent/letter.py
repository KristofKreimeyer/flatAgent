from pathlib import Path

import anthropic

from .models import Listing

SYSTEM = (
    "Du schreibst Bewerbungs-Anschreiben für Mietwohnungen auf Deutsch. "
    "Verwende ausschließlich Fakten aus dem Profil und der Anzeige. "
    "Gib nur den Brieftext zurück, ohne Erklärungen."
)


def build_prompt(listing: Listing, config: dict) -> str:
    p = config["profile"]
    style = ""
    tf = config["letter"].get("template_file")
    if tf and Path(tf).exists():
        style = Path(tf).read_text(encoding="utf-8")
    return f"""Profil:
- Name: {p['name']}
- Beruf: {p['occupation']}
- Haushalt: {p['household']}
- Bruttojahreseinkommen: {p['income_yearly_gross']} €
- Haustiere: {p['pets']}
- Zusätzlich: {p.get('extra', '')}

Anzeige:
Titel: {listing.title}
Ort: {listing.location}
Zimmer: {listing.rooms}, Fläche: {listing.area_sqm} m², Warmmiete: {listing.rent_warm}, Kaltmiete: {listing.rent_cold}
Text: {listing.description[:2000]}

Ton: {config['letter']['tone']}

{style}

Schreibe das Anschreiben."""


def write_letter(listing: Listing, config: dict, client=None) -> str:
    client = client or anthropic.Anthropic()  # liest ANTHROPIC_API_KEY
    msg = client.messages.create(
        model=config["letter"]["model"],
        max_tokens=800,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(listing, config)}],
    )
    return msg.content[0].text.strip()
