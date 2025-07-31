from dataclasses import dataclass


@dataclass
class Booster:
    id: int = 0
    name: str = "Unknown Booster"
    code: str = "Unknown Code"
    dotggCode: str = "Unknown DotGG Code"
    setId: str = "Unknown Set ID"
