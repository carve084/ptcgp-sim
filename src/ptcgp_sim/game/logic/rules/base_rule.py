"""
Sometimes, a single command results in a complex sequence of events and rules. This class manages that sequence.
Responsibility:
    To handle multistep game processes. For example, resolving combat isn't just one thing. It's a sequence:
        1. Fire "Before Attack" triggers.
        2. Calculate damage (considering buffs/debuffs).
        3. Deal damage.
        4. Fire "After Damage" triggers.
        5. Check for deaths.
        6. Fire "On Death" triggers.
            The ActionResolver would have a method like resolve_combat(game_state, attack_event)
            that walks through this entire sequence, creating new events and consulting the RuleEngine
            at each step.

Why it's standard:
    It keeps the GameController clean.
    The GameController just says action_resolver.resolve_combat(...)
    instead of having that complex logic inside its own methods.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ptcgp_sim.game.logic.events import GameEvent
    from ptcgp_sim.game.logic.effects import Effect
    from ptcgp_sim.game.logic.game_state import GameState

class Rule:
    """
    Abstract base class for a single game rule.
    A rule is a piece of logic that says: "IF a condition is met, THEN produce these effects."
    """
    def condition(self, event: GameEvent, game_state: GameState) -> bool:
        """
        Determines if this rule should be triggered by the given event and game state.
        Returns True if the rule's conditions are met, False otherwise.
        """
        raise NotImplementedError

    def action(self, event: GameEvent, game_state: GameState) -> list[Effect]:
        """
        Generates a list of effects to be applied if the condition is met.
        Returns a list of Effect objects.
        """
        raise NotImplementedError