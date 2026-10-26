from dataclasses import dataclass


@dataclass
class Listing:
    source: str
    id: str
    title: str
    url: str
    rent_warm: float | None = None
    rent_cold: float | None = None
    rooms: float | None = None
    area_sqm: float | None = None
    location: str = ""
    description: str = ""

    @property
    def key(self) -> str:
        return f"{self.source}:{self.id}"
