import random
from dataclasses import dataclass, field

from ptcgp_sim.game.objects.card import Card


@dataclass
class Deck:
    cards: list[Card] = field(default_factory=list)

    def add(self, card):
        self.cards.append(card)

    def remove(self, card):
        self.cards.remove(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None

    def __len__(self):
        return len(self.cards)
