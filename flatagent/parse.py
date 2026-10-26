import re


def num(text: str | None) -> float | None:
    """'1.234,50 €' -> 1234.5, '3,5 Zi.' -> 3.5"""
    if not text:
        return None
    m = re.search(r"\d[\d.]*(?:,\d+)?", text)
    if not m:
        return None
    return float(m.group(0).replace(".", "").replace(",", "."))
