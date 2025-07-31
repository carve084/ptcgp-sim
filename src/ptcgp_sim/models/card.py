from dataclasses import dataclass, field

from .ability import Ability
from .attack import Attack
from .energy import Energy
from .rarity import Rarity
from .rule import Rule
from .set import Set
from .subtype import Subtype
from .supertype import Supertype


@dataclass
class CardData:
    id: int = 0
    code: str = "Unknown Code"
    set: Set | None = None
    local_id: int = 0
    name: str = "Unknown Card"
    supertype: Supertype | None = None
    illustrator: str = "Unknown Illustrator"
    image: str | None = None
    rarity: Rarity | None = None
    hp: int | None = None
    energy_type: Energy | None = None
    evolve_from: str | None = None
    text: str = "Unknown Text"
    stage: str | None = None
    weakness: Energy | None = None
    retreat_cost: int | None = None
    subtype: Subtype | None = None
    rule: Rule | None = None

    # Many-to-one relationships
    abilities: list[Ability] = field(default_factory=list)
    attacks: list[Attack] = field(default_factory=list)

    def __repr__(self):
        return f"({self.code}) {self.name}"
