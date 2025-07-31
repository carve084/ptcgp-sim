import uuid
from dataclasses import dataclass, field

from ptcgp_sim.game.objects.card import Card
from ptcgp_sim.models.energy import Energy
from ptcgp_sim.game.objects.deck import Deck
from ptcgp_sim.game.objects.energy_zone import EnergyZone
from ptcgp_sim.game.logic.game_log import GameLog


MAX_BENCH_SIZE = 3  # Maximum number of Pokémon on the bench
MAX_HAND_SIZE = 10  # Maximum number of cards in hand


@dataclass
class Player:
    # Player object attributes
    name: str
    deck: Deck
    log: GameLog

    # Unique identifier for the player instance
    instance_id: uuid.UUID = field(default_factory=uuid.uuid4)

    # Game state attributes
    active_pokemon: Card | None = None
    bench: list[Card | None] = field(default_factory=lambda: [None] * MAX_BENCH_SIZE)
    discard_pile: list[Card] = field(default_factory=list)
    discarded_energy: list[Energy] = field(default_factory=list)
    energy_zone: EnergyZone | None = None
    hand: list[Card] = field(default_factory=list)
    points: int = 0

    @property
    def all_zones(self):
        yield [self.active_pokemon]
        yield self.hand
        yield self.bench
        yield self.discard_pile

    # Deck mechanics
    def draw_card(self):
        # Check for full hand
        if len(self.hand) >= MAX_HAND_SIZE:
            if self.log:
                self.log.log_message(f"{self.name} could not draw because their hand is full.")
            return

        # Draw a card from the deck. If the deck is empty, notify the player.
        card = self.deck.draw()
        if card is None:
            if self.log:
                self.log.log_message(f"{self.name} has no cards left to draw.")
            return

        # Add the drawn card to the player's hand
        self.hand.append(card)
        if self.log:
            self.log.log_message(f"{self.name} drew card: {card}")

    def draw_cards(self, count: int):
        for _ in range(count):
            self.draw_card()

    # Active Pokémon mechanics
    def set_active_pokemon_from_hand(self, card_to_set: Card) -> bool:
        """
        Play a card from hand to the active spot.
        This should only be called at the start of the game.
        """
        if card_to_set not in self.hand:
            if self.log:
                self.log.log_message(f"ERROR: {card_to_set.name} is not in {self.name}'s hand.")
            return False

        self.hand.remove(card_to_set)
        self.active_pokemon = card_to_set
        card_to_set.subscribe_to_death(self.handle_card_death)
        if self.log:
            self.log.log_message(f"{self.name} set active Pokémon: {card_to_set.name}")
        return True

    # Bench mechanics
    def is_bench_full(self) -> bool:
        """Checks if there are any empty spots left on the bench."""
        return None not in self.bench

    def play_card_to_bench(self, card_to_play: Card, bench_index: int | None = None) -> bool:
        """Play a card from hand to the bench at the specified index."""
        if card_to_play not in self.hand:
            if self.log:
                self.log.log_message(f"ERROR: {card_to_play.name} is not in {self.name}'s hand.")
            return False

        if bench_index is not None:
            # --- Case 1: Player specifies a bench index ---
            if not (0 <= bench_index < MAX_BENCH_SIZE):
                if self.log:
                    self.log.log_message(f"Invalid index {bench_index}. Must be between 0 and {MAX_BENCH_SIZE - 1}.")
                return False
            if self.bench[bench_index] is not None:
                if self.log:
                    self.log.log_message(f"Bench index {bench_index} is already occupied by {self.bench[bench_index].name}.")
                return False
            target_index = bench_index
        else:
            try:
                target_index = self.bench.index(None)  # Find the first available spot
            except ValueError:
                if self.log:
                    self.log.log_message(f"{self.name} cannot play {card_to_play.name} to the bench. Bench is full.")
                return False

        self.hand.remove(card_to_play)
        self.bench[target_index] = card_to_play
        card_to_play.subscribe_to_death(self.handle_card_death)
        return True

    # Discard mechanics
    def discard_card_and_attachments(self, card: Card):
        """Discard a card with any attached energy and cards."""
        # Move the main card to the discard pile
        self.discard_pile.append(card)

        # Move any attached energy to the discarded energy list
        if card.attached_energy:
            self.discarded_energy.extend(card.attached_energy)
            card.attached_energy.clear()

        # Discard any attached cards (e.g., Trainer cards)
        if card.attached_cards:
            self.discard_pile += card.attached_cards
            card.attached_cards.clear()

        # TODO: Remove any effects associated with the card

    def handle_card_death(self, dead_card: Card):
        """Handle the death of a card, removing it from the active or bench position."""
        # Search the bench first
        for i, card_on_bench in enumerate(self.bench):
            if card_on_bench is dead_card:
                self.bench[i] = None
                self.discard_card_and_attachments(dead_card)
                dead_card.unsubscribe_from_death(self.handle_card_death)
                return

        # Check active Pokémon
        if dead_card is self.active_pokemon:
            # Activate on-death effects if any
            # TODO: Implement on-death effects
            # Remove the active Pokémon
            self.active_pokemon = None
            self.discard_card_and_attachments(dead_card)

            if self.log:
                self.log.log_message(f"{self.name}'s active Pokémon {dead_card.name} has been defeated.")
            if self.bench:
                # TODO: For now, promote the first benched Pokémon if available
                self.promote_from_bench(0)
            else:
                if self.log:
                    self.log.log_message(f"{self.name} has no benched Pokémon to promote.")
                # TODO: Broadcast that the player has no available Pokémon

    def attach_energy(self, target, bench_index=0):
        if not self.energy_zone.current:
            print(f"{self.name} has no available energy.")
            return

        # Only one energy from the energy zone can be attached per turn
        if target == "active" and self.active_pokemon:
            self.active_pokemon.attach_energy(self.energy_zone.current)
            if self.log:
                self.log.log_message(f"{self.name} attached {self.energy_zone.current} energy to active card " +
                             f"{self.active_pokemon.name}.")
            self.energy_zone.current = None
        elif target == "bench" and 0 <= bench_index < len(self.bench):
            self.bench[bench_index].attach_energy(self.energy_zone.current)
            if self.log:
                self.log.log_message(f"{self.name} attached {self.energy_zone.current} energy to benched card " +
                             f"{self.bench[bench_index].name}.")
            self.energy_zone.current = None
        else:
            print(f"Invalid energy attachment target: {target}, bench index: {bench_index} out of {len(self.bench)}")

    def promote_from_bench(self, index):
        if self.bench:
            if self.active_pokemon:
                # Swap bench and active
                card = self.active_pokemon
                self.active_pokemon = self.bench[index]
                self.bench[index] = card
            else:
                self.active_pokemon = self.bench.pop(index)
        else:
            print(f"{self.name} has no benched cards to promote.")

    def _attack_active(self, attack, opponent):
        if self.active_pokemon and attack in self.active_pokemon.get_available_attacks():
            damage = attack.get_damage()
            opponent.active_pokemon.current_hp -= damage
            if self.log:
                self.log.log_message(f"{self.name}'s {self.active_pokemon.name} attacked {opponent.active_pokemon.name} for " +
                    f"{damage} damage!")
                self.log.log_message(f"{opponent.active_pokemon.name} HP: {opponent.active_pokemon.current_hp}")

            if not opponent.active_pokemon.is_alive():
                if self.log:
                    self.log.log_message(f"{opponent.active_pokemon.name} is defeated!")
                self.points += 1
                opponent.discard(opponent.active_pokemon)
                opponent.active_pokemon = None
                if opponent.bench:
                    # For now, promote the first benched Pokémon if available
                    opponent.promote_from_bench(0)
        else:
            print(f"{self.name}'s active Pokémon cannot perform that attack.")

    def _attack_bench(self, attack, opponent, bench_index):
        if self.active_pokemon and attack in self.active_pokemon.get_available_attacks():
            damage = attack.get_damage()
            opponent.bench[bench_index].current_hp -= damage
            if self.log:
                self.log.log_message(f"{self.name}'s {self.active_pokemon.name} attacked {opponent.bench[bench_index].name} for " +
                    f"{damage} damage!")
            self.log.log_message(f"{opponent.active_pokemon.name} HP: {opponent.active_pokemon.current_hp}")

            if not opponent.bench[bench_index].is_alive():
                print(f"{opponent.bench[bench_index].name} is defeated!")
                self.points += 1
                opponent.discard(opponent.bench[bench_index])
                del opponent.bench[bench_index]

    def attack(self, attack, opponent, target, bench_index=0):
        if self.active_pokemon:
            if target == "active" and opponent.active_pokemon:
                # Active card attacks opponent's active card
                self._attack_active(attack, opponent)
            elif target == "bench" and 0 <= bench_index < len(opponent.bench):
                # Active card attacks opponent's benched card
                self._attack_bench(attack, opponent, bench_index)
            else:
                # How did we get here
                print(f"{self.name} tried to attack opponent's {target} card but it failed.")
        else:
            print("Attack not possible.")

    def discard(self, card):
        if card in self.hand:
            self.hand.remove(card)
        self.discard_pile.append(card)
        if card.supertype == "Pokemon" and card.attached_energy:
            self.discarded_energy.extend(card.attached_energy)
            card.attached_energy.clear()

    def has_cards(self):
        if self.active_pokemon or len(self.bench) > 0:
            return True
        return False

    def __repr__(self) -> str:
        bench_str_list = [c.name if c else '—EMPTY—' for c in self.bench]
        bench_str = ", ".join(bench_str_list)
        return (f"\n"
            f"--- Player: {self.name} ---\n"
            f"  Hand: {[c.name for c in self.hand]}\n"
            f"  Active: {self.active_pokemon.name if self.active_pokemon else '—NONE—'}\n"
            f"  Bench: [{bench_str}]\n"
            f"  Discard: {[c.name for c in self.discard_pile]}\n"
            f"--------------------"
        )
