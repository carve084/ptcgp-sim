from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

from ptcgp_sim.game.logic.game_state import GameState
from ptcgp_sim.game.logic.rule_engine import RuleEngine
from ptcgp_sim.game.logic.action_resolver import ActionResolver
from ptcgp_sim.game.logic.game_log import GameLog
from ptcgp_sim.game.logic.events import TurnStartEvent

if TYPE_CHECKING:
    from ptcgp_sim.game.objects.player import Player


class GameController:
    """
    The central mediator and public API for the game logic. It receives high-level
    commands and uses its child components to execute them.
    """

    def __init__(self, players: list[Player]):
        self.game_state = GameState(players)
        self.rule_engine = RuleEngine()
        self.action_resolver = ActionResolver(self.rule_engine)
        self.game_log = GameLog()
        print("GameController initialized.")

    def start_game(self):
        """Starts the game and the first turn."""
        print("===== GAME START =====")
        self.start_turn()

    def start_turn(self):
        """Begins the current player's turn."""
        player = self.game_state.current_player
        print(f"\n--- Turn {self.game_state.turn_number}: {player.name}'s Turn ---")

        # Create and log the event
        event = TurnStartEvent(player)
        self.game_log.log_event(event)

        # Process any "start of turn" rules
        effects = self.rule_engine.process_event(event, self.game_state)
        for effect in effects:
            effect.apply(self.game_state)

    def request_end_turn(self):
        """
        Public method for a player to request the end of their turn.
        The UI/AI layer would call this when the player is done with their actions.
        """
        print(f"[CONTROLLER] {self.game_state.current_player.name} has ended their turn.")

        # 1. Increment turn number and switch players
        self.game_state.turn_number += 1
        self.game_state.current_player_index = (self.game_state.current_player_index + 1) % len(self.game_state.players)

        # 2. Start the next player's turn
        self.start_turn()

    def request_attack(self, attacker_id: uuid.UUID, defender_id: uuid.UUID, attack):
        """
        Public method for a player to request an attack.
        The UI/AI layer would call this with the instance_ids of the cards.
        """
        # 1. Validation
        attacker = self.game_state.find_object_by_id(attacker_id)
        defender = self.game_state.find_object_by_id(defender_id)

        # Add checks: Is it the right player's turn? Can the card attack?
        if not all([attacker, defender]):
            print("[CONTROLLER] Invalid attack request: Card(s) not found.")
            return

        # 2. Delegation
        # The controller doesn't know the details of combat; it tells the resolver to handle it.
        self.action_resolver.resolve_attack(self.game_state, attacker, defender, attack)
