from __future__ import annotations
from typing import TYPE_CHECKING

from ptcgp_sim.game.logic.rules.base_rule import Rule
from ptcgp_sim.game.logic.rules.damage_rules import BaseDamageRule

if TYPE_CHECKING:
    from ptcgp_sim.game.logic.events import GameEvent
    from ptcgp_sim.game.logic.effects import Effect
    from ptcgp_sim.game.logic.game_state import GameState


class RuleEngine:
    """
    The brain of the game's logic. It holds all active rules and processes
    events to determine which rules' actions should be executed.
    """

    def __init__(self):
        self.rules: list[Rule] = []
        self._load_rules()

    def _load_rules(self):
        """Loads all the rule objects into the engine."""
        # In a real system, you would discover and instantiate rules automatically
        # or from a configuration file.
        # self.rules.append(VengefulSpiritRule())
        self.rules = [
            BaseDamageRule(),
        ]
        print(f"\nRule engine loaded {len(self.rules)} rules.")

    def process_event(self, event: GameEvent, game_state: GameState) -> list[Effect]:
        """
        Takes an event, evaluates it against all rules, and returns a list
        of effects from all the rules that were triggered.
        """
        triggered_effects: list[Effect] = []
        print(f"[RULE ENGINE] Processing event: {event.name}")

        for rule in self.rules:
            if rule.condition(event, game_state):
                effects = rule.action(event, game_state)
                triggered_effects.extend(effects)
                print(f"[RULE ENGINE] Rule '{rule.__class__.__name__}' triggered.")

        return triggered_effects