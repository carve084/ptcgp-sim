import pytest
import psycopg2
from ptcgp_sim.loaders import set, supertype, rarity, rule, subtype, booster
from ptcgp_sim.loaders.card_booster import load_card_boosters
from ptcgp_sim.loaders.card import load_cards
from ptcgp_sim.loaders.energy import load_energies
from ptcgp_sim.db import DatabaseConfig


def test_data_loading():
    config = DatabaseConfig()

    with psycopg2.connect(**config.dict()) as conn:
        print("\n=== Loading Cards ===")
        cards = load_cards(conn)
        assert len(cards) > 0, "No cards loaded from the database."
        print(f"Loaded {len(cards)} cards.")
        if cards:
            print(f"First card: {cards[0].name}")
            print(f"  Abilities: {[a.name for a in cards[0].abilities]}")
            print(f"  Attacks: {[a.name for a in cards[0].attacks]}")

        print("\n=== Loading Energies ===")
        energies = load_energies(conn)
        assert len(energies) > 0, "No energies loaded from the database."
        print(f"Loaded {len(energies)} energies.")
        if energies:
            print(f"First energy: {energies[0].name}")

        print("\n=== Loading Sets ===")
        sets = set.load_sets(conn)
        assert len(sets) > 0, "No sets loaded from the database."
        print(f"Loaded {len(sets)} sets.")

        print("\n=== Loading Other Tables ===")
        print(f"Loaded {len(booster.load_boosters(conn))} boosters.")
        print(f"Loaded {len(rule.load_rules(conn))} rules.")
        print(f"Loaded {len(rarity.load_rarities(conn))} rarities.")
        print(f"Loaded {len(subtype.load_subtypes(conn))} subtypes.")
        print(f"Loaded {len(supertype.load_supertypes(conn))} supertypes.")
        print(f"Loaded {len(load_card_boosters(conn))} card_booster entries.")
