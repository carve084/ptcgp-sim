import pytest
import psycopg2
from ptcgp_sim.db import DatabaseConfig
from ptcgp_sim.loaders.card import load_card_by_code
from ptcgp_sim.game.objects.card import Card


@pytest.fixture
def sample_card_data():
    config = DatabaseConfig()
    with psycopg2.connect(**config.dict()) as conn:
        return load_card_by_code(conn, "A1-001") # Bulbasaur


def test_card_instance_initialization(sample_card_data):
    """Tests that a CardInstance initializes correctly from its template."""
    # Arrange & Act
    card = Card(sample_card_data)

    # Assert
    assert card.name == "Bulbasaur"
    assert card.card_data is sample_card_data
    assert card.current_hp == 70
    assert card.instance_id is not None


def test_card_takes_non_lethal_damage(sample_card_data):
    """Tests that a card's health is correctly reduced by damage."""
    # Arrange
    card = Card(sample_card_data)

    # Act
    card.take_damage(60)

    # Assert
    assert card.current_hp == 10


def test_card_death_event_fires_on_lethal_damage(sample_card_data):
    """
    Tests the crucial event-firing mechanism when a card dies.
    This demonstrates how to test an event system with a mock handler.
    """
    # Arrange
    card = Card(sample_card_data)

    # Create a simple "spy" or mock handler to track if the event was called.
    mock_handler_state = {"called": False, "dead_card": None}

    def mock_death_handler(dead_card):
        mock_handler_state["called"] = True
        mock_handler_state["dead_card"] = dead_card

    card.subscribe_to_death(mock_death_handler)

    # Act
    card.take_damage(80)  # More than enough to be lethal

    # Assert
    assert card.current_hp <= 0
    assert mock_handler_state["called"] is True
    # Check that the event passed the correct instance back to the handler
    assert mock_handler_state["dead_card"] is card