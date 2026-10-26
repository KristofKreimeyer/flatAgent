from .models import Listing


def matches(listing: Listing, search: dict) -> bool:
    """True, wenn das Angebot zu den Suchkriterien passt.

    Unbekannte Werte (None) lassen wir durch, damit nichts Gutes durch
    schlechtes Parsen verloren geht. Der Nutzer sieht ja die Mail.
    """
    if listing.rooms is not None:
        if not search["rooms_min"] <= listing.rooms <= search["rooms_max"]:
            return False

    rent = listing.rent_warm
    if rent is None and listing.rent_cold is not None:
        # Kaltmiete allein: Nebenkosten grob mit 2,5 €/m² oder 150 € ansetzen
        rent = listing.rent_cold + (2.5 * listing.area_sqm if listing.area_sqm else 150)
    if rent is not None and rent > search["max_rent_warm"]:
        return False

    haystack = f"{listing.title} {listing.description}".lower()
    if any(k.lower() in haystack for k in search.get("exclude_keywords", [])):
        return False

    places = [p.lower() for p in search.get("allowed_places", [])]
    if places and listing.location:
        loc = f"{listing.location} {listing.title}".lower()
        if not any(p in loc for p in places):
            return False
    return True
