from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from ptcgp_sim.game.logic.game_state import GameState

class Effect:
    """
    Base class for an action that modifies the game state.
    This defines what it means to modify the game state.
    It will represent the outcome of a rule's action. An Effect is a command object that changes the GameState.
        - ModifyHealthEffect(target_id, amount)
        - DrawCardEffect(player_id, count)
        - ApplyTemporaryStatBuffEffect(target_id, stat, amount, duration)
    The action method of a Rule would create one of these Effect objects,
    and a central function would be responsible for applying it to the GameState.
    This makes the change explicit and loggable.
    It separates the decision to do something (the Rule) from the act of doing it (the Effect),
    which is a powerful separation of concerns.
    """
    def apply(self, game_state: GameState):
        """Applies the effect to the given game state."""
        raise NotImplementedError("Subclasses must implement the apply method.")

class DealDamageEffect(Effect):
    def __init__(self, target_id: uuid.UUID, amount: int, source_id: uuid.UUID | None = None):
        self.target_id = target_id
        self.amount = amount
        self.source_id = source_id

    def apply(self, game_state: GameState):
        target = game_state.find_object_by_id(self.target_id)
        if target and hasattr(target, 'take_damage'):
            # In a real implementation, you would queue a DamageDealtEvent here.
            target.take_damage(self.amount)
            print(f"[EFFECT] Dealt {self.amount} damage to {target.name}.")

class DrawCardEffect(Effect):
    def __init__(self, player_id: uuid.UUID, count: int = 1):
        self.player_id = player_id
        self.count = count

    def apply(self, game_state: GameState):
        player = game_state.find_object_by_id(self.player_id)
        if player:
            player.draw_cards(self.count)
            print(f"[EFFECT] Player {player.name} drew {self.count} card(s).")
