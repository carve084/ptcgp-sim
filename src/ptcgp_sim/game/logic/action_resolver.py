from __future__ import annotations
from typing import TYPE_CHECKING

from ptcgp_sim.game.logic.events import GameEvent, AttackDeclaredEvent, DamageDealtEvent, TurnEndEvent

if TYPE_CHECKING:
    from ptcgp_sim.game.logic.game_state import GameState
    from ptcgp_sim.game.logic.rule_engine import RuleEngine
    from ptcgp_sim.game.objects.player import Player
    from ptcgp_sim.game.objects.card import Card
    # TODO: Change Attack to AttackData, create game.objects.attack, and import it from there
    from ptcgp_sim.models.attack import Attack


class ActionResolver:
    """
    Handles complex, multi-stage game actions by orchestrating
    the creation of events and the application of effects.
    """

    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
        # This will hold effects that need to be applied after processing an event chain
        self.effect_queue = []

    def resolve_attack(self, game_state: GameState, attacker: Card, defender: Card, attack: Attack):
        """Orchestrates the entire combat sequence."""
        print(f"\n--- Resolving Attack: {attacker.name} vs {defender.name} ---")

        # 1. Announce the attack
        attack_event = AttackDeclaredEvent(attacker, defender, attack)
        # Process rules that trigger on attack declaration (e.g., "Taunt")
        self.process_and_apply_effects(attack_event, game_state)

        # 2. Calculate damage (could be its own complex step)
        damage_amount = attack.get_damage()

        # 3. Create and process damage event
        damage_event = DamageDealtEvent(source=attacker, target=defender, amount=damage_amount)
        self.process_and_apply_effects(damage_event, game_state)

        # In a real game, the defender would also attack back.
        print("--- Attack Resolution Complete ---")

    def resolve_end_turn(self, game_state: GameState):
        """
        Resolves the end of a player's turn.
        For now, simply advance the game state to the next player's turn.
        """
        print(f"\n--- Resolving End Turn for Player: {game_state.current_player.name} ---")

        # Process any end-of-turn effects
        end_turn_event = TurnEndEvent(player=game_state.current_player)
        self.process_and_apply_effects(end_turn_event, game_state)

        # Advance the turn
        game_state.advance_turn()
        print("--- End Turn Resolution Complete ---")

    def resolve_draw(self, game_state: GameState, player: Player):
        """
        Resolves the draw phase for a player.
        This is where the player draws cards from their deck.
        """
        print(f"\n--- Resolving Draw Phase for Player: {player.name} ---")

        # Draw a card
        drawn_card = player.draw_card()
        if drawn_card:
            print(f"{player.name} drew {drawn_card.name}.")
            # Process any effects that trigger on drawing a card
            self.process_and_apply_effects(drawn_card.on_draw_event(), game_state)
        else:
            print(f"{player.name} cannot draw a card; their deck is empty.")

        print("--- Draw Phase Resolution Complete ---")

    def process_and_apply_effects(self, event: GameEvent, game_state: GameState):
        """Helper to process an event with the rule engine and apply resulting effects."""
        effects = self.rule_engine.process_event(event, game_state)
        for effect in effects:
            effect.apply(game_state)
