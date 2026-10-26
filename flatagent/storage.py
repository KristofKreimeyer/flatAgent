import json
from pathlib import Path


class SeenStore:
    """Merkt sich bereits gemeldete Angebote in einer JSON-Datei."""

    def __init__(self, path: str | Path = "state/seen.json"):
        self.path = Path(path)
        self.seen: set[str] = set()
        if self.path.exists():
            self.seen = set(json.loads(self.path.read_text(encoding="utf-8")))

    def is_new(self, key: str) -> bool:
        return key not in self.seen

    def add(self, key: str) -> None:
        self.seen.add(key)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(sorted(self.seen), indent=0), encoding="utf-8")
