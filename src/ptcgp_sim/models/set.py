from dataclasses import dataclass


@dataclass
class Set:
    id: int = 0
    code: str | None = None
    name: str = "Unknown Set"
    card_count_official: int | None = None
    card_count_total: int | None = None
    logo: str | None = None
    symbol: str | None = None
