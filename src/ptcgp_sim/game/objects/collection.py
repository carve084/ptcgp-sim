import psycopg2
from dataclasses import dataclass, field

from ptcgp_sim.db import DatabaseConfig
from ptcgp_sim.loaders.card import load_cards
from ptcgp_sim.models.card import CardData


@dataclass
class Collection:
    cards: dict = field(default_factory=dict)

    def add(self, card: CardData):
        """Add a card to the collection."""
        if card.id not in self.cards:
            self.cards[card.id] = card
        else:
            print(f"Card {card.name} already exists in the collection.")

    def fill(self):
        """Fill the collection with cards."""
        config = DatabaseConfig()
        with psycopg2.connect(**config.dict()) as conn:
            all_card_data = load_cards(conn)
            for card_data in all_card_data:
                self.add(card_data)

    def get(self, card_id: int) -> CardData:
        """Get a card by its card id."""
        return self.cards[card_id]

    def get_by_name(self, name: str) -> list[CardData]:
        """Get cards by their name."""
        return [card for card in self.cards.values() if card.name.lower() == name.lower()]

    def __len__(self):
        """Return the number of cards in the collection."""
        return len(self.cards)
