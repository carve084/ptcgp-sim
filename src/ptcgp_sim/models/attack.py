import re
from dataclasses import dataclass


@dataclass
class Attack:
    id: int = 0
    card_id: int = 0
    costs: str | None = None
    name: str = "Unknown Attack"
    effect: str | None = None
    damage: str | None = None

    def __str__(self):
        return f"""{{{self.costs}}} {self.name}{' ' + self.damage if self.damage else ''}{': ' + self.effect if self.effect else ''}"""

    def get_damage(self):
        """Returns the numeric portion of the damage string as an int, or 0 if none is found."""
        if not self.damage:
            return 0
        match = re.search(r'\d+', self.damage)
        return int(match.group()) if match else 0
