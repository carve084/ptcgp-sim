import pytest
import psycopg2
import random

from ptcgp_sim.game.objects.player import Player
from ptcgp_sim.setup.setup_player import setup_player
from ptcgp_sim.loaders.card import load_cards, load_card_by_code
from ptcgp_sim.loaders.energy import load_energies
from ptcgp_sim.game.objects.card import Card
from ptcgp_sim.game.objects.deck import Deck
from ptcgp_sim.game.logic.game_log import GameLog
from ptcgp_sim.db import DatabaseConfig


@pytest.fixture
def player_setup():
    """Fixture to set up a player and some distinct card instances."""
    config = DatabaseConfig()
    with psycopg2.connect(**config.dict()) as conn:
        bulbasaur_data = load_card_by_code(conn, "A1-001")  # Load Bulbasaur card data
        charmander_data = load_card_by_code(conn, "A1-033")  # Load Charmander card data

    # Create distinct card instances
    bulbasaur1 = Card(bulbasaur_data)
    bulbasaur2 = Card(bulbasaur_data)
    charmander = Card(charmander_data)

    player = Player(name="Ash", deck=Deck([]), log=GameLog())
    player.hand = [bulbasaur1, bulbasaur2, charmander]  # Add distinct cards to the player's hand

    return player, bulbasaur1, bulbasaur2, charmander


def test_player_play_card_to_bench(player_setup):
    """Tests moving a card from hand to the first available bench spot."""
    # Arrange
    player, bulbasaur1, _, _ = player_setup
    assert len(player.hand) == 3
    assert player.bench[0] is None

    # Act
    success = player.play_card_to_bench(bulbasaur1)

    # Assert
    assert success is True
    assert len(player.hand) == 2
    assert bulbasaur1 not in player.hand
    assert player.bench[0] is bulbasaur1


def test_player_handles_duplicate_card_death_correctly(player_setup):
    """
    This is a critical test. It ensures that when one of two identical cards
    dies, ONLY that specific instance is removed from the correct bench slot.
    """
    # Arrange
    player, bulbasaur1, bulbasaur2, _ = player_setup

    # Play both identical dragons to the bench
    player.play_card_to_bench(bulbasaur1)  # Goes to spot 0
    player.play_card_to_bench(bulbasaur2)  # Goes to spot 1

    assert player.bench[0] is bulbasaur1
    assert player.bench[1] is bulbasaur2
    assert len(player.discard_pile) == 0

    # Act
    # Simulate the death of ONLY the second dragon instance.
    # The player's handle_card_death method will be called via the event system.
    bulbasaur2.take_damage(1000)

    # Assert
    assert len(player.discard_pile) == 1
    # Check that the exact instance that died is in the graveyard
    assert player.discard_pile[0] is bulbasaur2
    # Check that the bench slot is now empty
    assert player.bench[1] is None
    # CRUCIALLY, check that the other identical dragon is untouched
    assert player.bench[0] is bulbasaur1


class TestPlayerSetup():
    def test_basic_player_setup(self):
        config = DatabaseConfig()

        with psycopg2.connect(**config.dict()) as conn:
            all_card_data = load_cards(conn)
            all_energies = load_energies(conn)

            # Create a mock deck with 20 cards
            cards = [Card(c) for c in all_card_data if c.supertype and c.supertype.name == "Pokemon"]
            assert len(cards) >= 20, "Not enough Pokémon cards for test."
            test_deck = Deck(cards=random.sample(cards, 20))

            # Run setup
            log = GameLog()
            player = setup_player(name="Ash", deck=test_deck, available_energy_types=all_energies, log=log)

            assert "drew card" in log.get_last(5)[0].message  # Check if the log contains a draw action
            assert player.name == "Ash"
            assert len(player.deck.cards) == 15  # 20 cards minus 5 drawn for starting hand
            assert 1 <= len(player.hand) <= 5
            assert player.energy_zone.next in player.energy_zone.allowed_types
            assert 1 <= len(player.energy_zone.allowed_types) <= 3
