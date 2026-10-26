# flatAgent

Sucht neue Mietwohnungen (3 Zimmer, bis 850 € warm, Holzwickede + ca. 6 km), schreibt mit Claude ein
passendes Anschreiben und schickt dir beides per Mail. Der Agent sendet nichts an Vermieter.

## Ablauf
`sources/` holt Angebote → `filters.py` prüft sie gegen `config.yaml` → `storage.py` merkt sich Bekanntes
(`state/seen.json`) → `letter.py` erzeugt das Anschreiben → `mailer.py` verschickt einen Digest.

## Anpassen
- Kriterien, Profil, Ton, Empfänger: `config.yaml`
- Stilvorgaben fürs Anschreiben: `letter_template.txt`
- Neue Quelle: Modul in `flatagent/sources/` mit `fetch(search) -> list[Listing]` anlegen und in `sources/__init__.py` eintragen.

## Lokal ausprobieren
```
pip install -e ".[dev]"
pytest
export ANTHROPIC_API_KEY=...
python -m flatagent.main --dry-run   # gibt die Mail aus, sendet und speichert nichts
```

## Betrieb auf GitHub Actions
Repo-Secrets setzen: `ANTHROPIC_API_KEY`, `SMTP_USER`, `SMTP_PASSWORD` (bei Gmail ein App-Passwort).
Der Workflow `search.yml` läuft alle 20 Minuten und committet `state/seen.json` zurück.

## Bekannte Grenzen
Die Seiten-Parser (Selektoren) sind nur gegen Test-HTML geprüft, nicht gegen die Live-Seiten, und können
nach Änderungen der Portale brechen. ImmoScout24 blockt Bots oft. Fehlschläge einer Quelle werden geloggt
und stoppen die anderen nicht.
