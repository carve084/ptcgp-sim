from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import uuid

# Use a forward reference to avoid circular imports. Python's type checker
# will resolve this at type-checking time.
if TYPE_CHECKING:
    # TODO: Change Attack to AttackData, create game.objects.attack, and import it from there
    from ptcgp_sim.models.attack import Attack
    from ptcgp_sim.game.objects.card import Card
    from ptcgp_sim.game.objects.player import Player

class GameEvent:
    """Base class for all events in the game."""
    def __init__(self):
        self.event_id = uuid.uuid4()
        self.timestamp = datetime.now()
        self.name = self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.name}>"

class TurnStartEvent(GameEvent):
    """Fired at the very beginning of a turn."""
    def __init__(self, player: Player):
        super().__init__()
        self.player = player

class TurnEndEvent(GameEvent):
    """Fired at the end of a player's turn."""
    def __init__(self, player: Player):
        super().__init__()
        self.player = player

class AttackDeclaredEvent(GameEvent):
    """Fired when a player declares an intention to attack."""
    def __init__(self, attacker: Card, defender: Card, attack: Attack):
        super().__init__()
        self.attacker = attacker
        self.defender = defender
        self.attack = attack

class DamageDealtEvent(GameEvent):
    """Fired after damage is calculated and applied."""
    def __init__(self, source: Card | None, target: Card | Player, amount: int):
        super().__init__()
        self.source = source
        self.target = target
        self.amount = amount

class CardDiedEvent(GameEvent):
    """Fired when a card's health is reduced to 0 or less."""
    def __init__(self, card: Card):
        super().__init__()
        self.card = card
