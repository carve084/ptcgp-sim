from ptcgp_sim.models.card import CardData
from ptcgp_sim.loaders.card import load_cards

class CardRegistry:
    def __init__(self):
        self._cards_by_code: dict[str, CardData] = {}
        self._cards_by_id: dict[int, CardData] = {}

    def load(self, conn):
        """Loads all cards into the registry using the efficient loader."""
        all_cards = load_cards(conn)
        for card in all_cards:
            self._cards_by_code[card.code] = card
            self._cards_by_id[card.id] = card
        print(f"CardRegistry loaded with {len(all_cards)} cards.")

    def get_by_code(self, code: str) -> CardData | None:
        return self._cards_by_code.get(code)

    def get_by_id(self, id: int) -> CardData | None:
        return self._cards_by_id.get(id)
