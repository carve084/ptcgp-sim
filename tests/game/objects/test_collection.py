import unittest

from ptcgp_sim.game import Collection

# TODO: Unused for now

class TestCollection(unittest.TestCase):
    def test_collection_initialization(self):
        """Test if the collection initializes correctly."""
        collection = Collection()
        collection.fill()
        self.assertIsNotNone(collection.cards, "Collection should not be None after initialization.")
        self.assertGreater(len(collection.cards), 0, "Collection should contain cards after filling.")
        print(f"Collection initialized with {len(collection.cards)} cards.")

    def test_get_cards_by_name(self):
        """Test if cards can be retrieved by name."""
        collection = Collection()
        collection.fill()
        card_name = "Pikachu"
        cards = collection.get_by_name(card_name)
        self.assertIsInstance(cards, list, "Should return a list of cards.")
        print(f"Retrieved {len(cards)} cards with name '{card_name}' from the collection.")
        for card in cards:
            print(card)
