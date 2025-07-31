from __future__ import annotations
from typing import TYPE_CHECKING

# Import the necessary components from the logic layer
from ptcgp_sim.game.logic.rules.base_rule import Rule
from ptcgp_sim.game.logic.events import DamageDealtEvent  # This is the primary event we listen for
from ptcgp_sim.game.logic.effects import Effect, DealDamageEffect

if TYPE_CHECKING:
    from ptcgp_sim.game.logic.events import GameEvent
    from ptcgp_sim.game.logic.game_state import GameState


# -----------------------------------------------------------------------------
# 1. THE FUNDAMENTAL RULE: APPLYING DAMAGE
# -----------------------------------------------------------------------------

class BaseDamageRule(Rule):
    """
    This is the most fundamental damage rule. It's responsible for converting
    a DamageDealtEvent into an actual DealDamageEffect that modifies a card's health.

    This might seem redundant, but it decouples the *announcement* of damage
    from the *application* of damage, allowing other rules to intercept and modify it.
    """

    def condition(self, event: GameEvent, game_state: GameState) -> bool:
        # This rule triggers whenever damage is dealt to a card.
        return isinstance(event, DamageDealtEvent) and hasattr(event.target, 'card_data')

    def action(self, event: DamageDealtEvent, game_state: GameState) -> list[Effect]:
        # The action is to create an effect that formally applies the damage.
        # In a more advanced system, this effect might be intercepted again.
        print(f"[RULE] BaseDamageRule: Applying {event.amount} damage to {event.target.name}.")
        return [
            DealDamageEffect(
                target_id=event.target.instance_id,
                amount=event.amount,
                source_id=event.source.instance_id if event.source else None
            )
        ]