# Responsibility: To be the single, authoritative container for the entire current state of a single game match. It holds references to the players, the current turn number, whose turn it is, etc. It should be easily serializable (convertible to JSON), which is a massive benefit for saving/loading games, replays, and debugging.
# Why it's standard: It creates a "single source of truth." The GameController and RuleEngine act upon the GameState but don't own it. This makes your logic much cleaner and easier to test—you can create a GameState object representing a specific scenario and pass it to your logic functions.
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from ptcgp_sim.game.objects.player import Player
    from ptcgp_sim.game.objects.card import Card


class GameState:
    """
    A container for the entire state of a single game. This object is the
    "single source of truth" that logic functions read from and modify.
    """

    def __init__(self, players: list[Player]):
        self.game_id = uuid.uuid4()
        self.players = players
        self.current_player_index = 0
        self.turn_number = 1
        self.is_game_over = False

        print(f"GameState created for game {self.game_id}.")

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def advance_turn(self):
        """Advances the game to the next player's turn."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            # If we wrapped around, increment the turn number
            self.turn_number += 1

    def find_object_by_id(self, object_id: uuid.UUID) -> Player | Card | None:
        """Searches all players and their zones for an object with the given ID."""
        # This is a critical utility for effects and rules to find their targets.
        for player in self.players:
            if player.instance_id == object_id:
                return player

            for zone in player.all_zones:
                for card in zone:
                    if card is not None and card.instance_id == object_id:
                        return card
        return None
