from dataclasses import dataclass


@dataclass
class CardBooster:
    card_id: int | None = None
    booster_id: int | None = None
