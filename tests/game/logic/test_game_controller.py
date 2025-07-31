import pytest
import psycopg2

from ptcgp_sim.db import DatabaseConfig
from ptcgp_sim.data.registry import CardRegistry
from ptcgp_sim.game.objects.card import Card
from ptcgp_sim.game.objects.deck import Deck
from ptcgp_sim.game.objects.player import Player
from ptcgp_sim.game.logic.game_log import GameLog
from ptcgp_sim.game.logic.game_controller import GameController


@pytest.fixture
def full_game_setup():
    """
    A comprehensive fixture that sets up a ready-to-play game scenario.
    This is invaluable for testing high-level interactions.
    """
    # Load the card registry
    card_registry = CardRegistry()
    config = DatabaseConfig()
    with psycopg2.connect(**config.dict()) as conn:
        card_registry.load(conn)

    # Create card templates
    bulbasaur_data = card_registry.get_by_code("A1-001")
    charmander_data = card_registry.get_by_code("A1-033")

    # Create decks
    p1_deck = Deck([Card(bulbasaur_data) for _ in range(5)])
    p2_deck = Deck([Card(charmander_data) for _ in range(5)])

    # Create log
    log = GameLog()

    # Create players
    player1 = Player("Alice", p1_deck, log)
    player2 = Player("Bob", p2_deck, log)

    # Put some cards in play for an immediate test scenario
    player1.draw_cards(2)
    player1.set_active_pokemon_from_hand(player1.hand[0])  # A Bulbasaur
    player1.play_card_to_bench(player1.hand[0])

    player2.draw_cards(2)
    player2.set_active_pokemon_from_hand(player2.hand[0])  # A Charmander
    player2.play_card_to_bench(player2.hand[0])

    # Create the controller
    controller = GameController([player1, player2])

    return controller, player1, player2


def test_game_controller_attack_non_lethal(full_game_setup):
    """Tests a full attack sequence where both cards survive."""
    # Arrange
    controller, player1, player2 = full_game_setup
    bulbasaur = player1.active_pokemon
    charmander = player2.active_pokemon

    vine_whip = next((a for a in bulbasaur.attacks if a.name == "Vine Whip"), None)
    assert vine_whip is not None, "Test setup failed: Vine Whip attack not found."

    charmander_initial_health = charmander.current_hp
    vine_whip_damage = vine_whip.get_damage()

    # Act
    # The UI/AI would call this with the unique instance IDs of the cards.
    controller.request_attack(bulbasaur.instance_id, charmander.instance_id, vine_whip)

    # Assert
    # Bulbasaur (Vine Whip: 40 damage) hits Charmander (60 hp). Charmander takes 40 damage.
    assert charmander_initial_health == 60
    assert vine_whip_damage == 40
    assert charmander.current_hp == charmander_initial_health - vine_whip_damage
