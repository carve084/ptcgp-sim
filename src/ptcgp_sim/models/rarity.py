from dataclasses import dataclass


@dataclass
class Rarity:
    id: int = 0
    symbol: str = "Unknown Symbol"
    name: str = "Unknown Rarity"
    dotggName: str = "Unknown DotGG Name"
    code: str = "Unknown Code"

    def __str__(self):
        return f"{self.symbol}"
