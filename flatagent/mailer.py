import html
import os
import smtplib
from email.message import EmailMessage

from .models import Listing


def render(items: list[tuple[Listing, str]]) -> tuple[str, str]:
    """Gibt (Betreff, Text) zurück."""
    subject = f"flatAgent: {len(items)} neue Wohnung(en)"
    parts = []
    for l, letter in items:
        miete = f"{l.rent_warm:.0f} € warm" if l.rent_warm else (f"{l.rent_cold:.0f} € kalt" if l.rent_cold else "Miete unbekannt")
        parts.append(
            f"{l.title}\n{l.location} | {l.rooms or '?'} Zi. | {l.area_sqm or '?'} m² | {miete}\n"
            f"{l.url}\n\n--- Anschreiben ---\n{letter}\n"
        )
    return subject, ("\n" + "=" * 60 + "\n\n").join(parts)


def send(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = to
    msg.set_content(body)
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    with smtplib.SMTP_SSL(host, port) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        s.send_message(msg)
