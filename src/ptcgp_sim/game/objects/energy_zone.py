import random
from dataclasses import dataclass
from typing import List
from ptcgp_sim.models.energy import Energy


DISALLOWED_ENERGY_TYPES = [
    "Dragon",
    "Colorless"
]  # Energy types that cannot be used in EnergyZone

@dataclass
class EnergyZone:
    allowed_types: List[Energy]  # 1 to 3 elements
    current: Energy | None = None
    next: Energy | None = None

    def __post_init__(self):
        if not (1 <= len(self.allowed_types) <= 3):
            raise ValueError("EnergyZone must have between 1 and 3 energy types.")
        if any(energy.name in DISALLOWED_ENERGY_TYPES for energy in self.allowed_types):
            raise ValueError(f"Energy types {DISALLOWED_ENERGY_TYPES} are not allowed in EnergyZone.")
        self.roll_initial()

    def roll_initial(self):
        self.next = random.choice(self.allowed_types)

    def advance_turn(self):
        """Call at the start of each turn to rotate energy."""
        self.current = self.next
        self.next = random.choice(self.allowed_types)
