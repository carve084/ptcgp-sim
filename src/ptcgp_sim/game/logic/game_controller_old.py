from ptcgp_sim.game.objects.player import Player
from ptcgp_sim.game.objects.card import Card
from ptcgp_sim.game.logic.rule_engine import RuleEngine
from ptcgp_sim.game.logic.events import GameEvent
from ptcgp_sim.game.logic.game_log import GameLog


class GameController:
    """
    The primary public API for the game logic. The UI or AI layers only talk to the GameController.
    It takes high-level commands, validates them, creates the appropriate GameEvent,
    and starts the resolution process. It orchestrates the other logic components.
    """
    def __init__(self, player1: Player, player2: Player, log: GameLog):
        self.players = [player1, player2]
        self.turn = 1
        self.log = log
        self.rule_engine = RuleEngine(self)

        # Attach log to players
        for player in self.players:
            player.log = self.log

    @property
    def current_player(self) -> Player:
        return self.players[self.turn % 2]

    @property
    def opponent(self) -> Player:
        return self.players[(self.turn + 1) % 2]

    def start_game(self):
        max_turns = 100
        self.log.log("Game started!")
        self.play_first_turn()
        while not self.game_over() and self.turn < max_turns:
            self.play_turn()

        winner = self.get_winner()
        if winner:
            self.log.log(f"🏆 {winner.name} wins the game with {winner.points} points!")
        else:
            self.log.log("Game ended in a draw.")

    def request_play_card(self, player: Player, hand_index: int, bench_index: int | None):
        """
        Handles a player's request to play a card from their hand to the bench.
        """
        card_played = player.play_card_to_bench(hand_index, bench_index)

        if card_played:
            card_played.subscribe_to_death(self.game_master_card_death_handler)

    def request_attack(self, attacker: Card, defender: Card):
        """
        Handles a player's request to attack with a Pokémon.
        """
        player = self.current_player

        if not player.active_pokemon or player.active_pokemon is not attacker:
            self.log.log(f"{player.name} cannot attack with {attacker.name} because it is not active.")
            return

        # Perform the attack


    def play_first_turn(self):
        """
        Handles the first turn of the game, where the first player cannot attack.
        """
        player = self.current_player
        self.log.log(f"\n=== {player.name}'s first turn begins ===")

        # 1. Draw a card
        player.draw_card()

        # 2. Main phase: play cards, attach energy, but cannot attack
        self.log.log(f"{player.name} takes their main phase actions... (placeholder)")

        # 3. End Turn
        self.log.log(f"=== {player.name}'s turn ends ===\n")
        self.turn += 1


    def play_turn(self):
        player = self.current_player
        opponent = self.opponent

        self.log.log(f"=== {player.name}'s turn begins ===")

        # 1. Advance Energy Zone
        player.energy_zone.advance_turn()
        self.log.log(f"{player.name}'s energy: current = {player.energy_zone.current}, next = {player.energy_zone.next}")

        # 2. Draw a card
        player.draw_card()

        # 3. Main phase: play cards, attach energy, attack
        # TODO: Add logic for trainer cards, abilities, etc.
        self.log.log(f"{player.name} takes their main phase actions... (placeholder)")  # Example game decisions
        player.attach_energy(target="active")
        if player.active_pokemon:
            attacks = player.active_pokemon.get_available_attacks()
            if attacks:
                player.attack(attack=attacks[0], opponent=opponent, target="active")
                self.rule_engine.handle_event(GameEvent(type='on_attack', source=player.active_pokemon, target=opponent.active_pokemon))
        else:
            self.log.log(f"{player.name} has no active Pokémon to attack with.")


        # 4. End Turn
        self.log.log(f"=== {player.name}'s turn ends ===\n")
        self.turn += 1

    def game_master_card_death_handler(self, dead_card):
        """
        Handles the death of a card, which may trigger abilities or game events.
        """
        dead_card.unsubscribe_from_death(self.game_master_card_death_handler)

    def game_over(self) -> bool:
        return any((not player.has_cards()) or player.points >= 3 for player in self.players)

    def get_winner(self) -> Player | None:
        winners = [p for p in self.players if p.has_cards() and p.points >= 3]
        return winners[0] if winners else None
