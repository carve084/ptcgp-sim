import random

from typing import Optional

from ptcgp_sim.models.energy import Energy
from ptcgp_sim.game.objects.player import Player
from ptcgp_sim.game.objects.deck import Deck
from ptcgp_sim.game.objects.energy_zone import EnergyZone
from ptcgp_sim.game.logic.game_log import GameLog


DISALLOWED_ENERGY_TYPES = [
    "Dragon",
    "Colorless"
]  # Energy types that cannot be used in EnergyZone

def setup_player(name: str, deck: Deck, available_energy_types: list[Energy], log: Optional[GameLog] = None) -> Player:
    if len(deck.cards) != 20:
        raise ValueError("Deck must contain exactly 20 cards.")

    # Ensure the deck contains at least one Basic Pokémon
    if not any(card.stage == "Basic" for card in deck.cards):
        raise ValueError("Deck must contain at least one Basic Pokémon.")

    # Energy zone setup
    available_energy_zone_types = [e for e in available_energy_types if e.name not in DISALLOWED_ENERGY_TYPES]

    # Choose 1–3 random energy types for this player's energy zone
    energy_zone = EnergyZone(allowed_types=random.sample(available_energy_zone_types, k=random.randint(1, 3)))

    player = Player(
        name=name,
        deck=deck,
        energy_zone=energy_zone,
        log=log
    )

    # Shuffle the deck
    player.deck.shuffle()

    # Step 1: Force the first card drawn to be a Basic Pokémon
    basic_card = None
    for i, card in enumerate(player.deck.cards):
        if card.stage == "Basic":
            basic_card = card
            break

    if basic_card is None:
        raise RuntimeError("Somehow failed to find a Basic card in deck, despite earlier check.")

    # Move the Basic to hand
    player.deck.cards.remove(basic_card)
    player.hand.append(basic_card)
    if log:
        log.log(f"{player.name} drew a (basic) card: {basic_card}")

    # Step 2: Draw remaining cards to fill hand to 5
    cards_needed = 5 - len(player.hand)
    player.draw_cards(cards_needed)

    # Step 3: Set active Pokémon to a Basic from hand
    for hand_index, card in enumerate(player.hand):
        if card.stage == "Basic":
            player.set_active_pokemon_from_hand(hand_index)
            if log:
                player.log.log(f"{player.name} set their active Pokémon to {card.name}.")
                player.log.log(f"{player}")
            break

    # Step 4: Fill bench with up to 3 other Basics
    hand_index = 0
    while not player.is_bench_full() and hand_index < len(player.hand):
        card = player.hand[hand_index]
        if card.stage == "Basic":
            player.play_card_to_bench(hand_index)
            if log:
                player.log.log(f"{player.name} added {card.name} to their bench.")
                player.log.log(f"{player}")
        else:
            hand_index += 1

    return player
