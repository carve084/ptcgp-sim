from dataclasses import dataclass


@dataclass
class Ability:
    id: int
    card_id: int
    name: str
    effect: str
    type: str | None = None  # e.g., 'triggered', 'activated'
    trigger: str | None = None  # e.g., 'on_play', 'on_attack'

    def __str__(self) -> str:
        return f"{self.name}: {self.effect}"
