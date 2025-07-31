import json
import re
import psycopg2

from ptcgp_sim.db import DatabaseConfig


# This script updates card and dependent tables using cards.json


# Constants
CARDS_FILE_PATH = "../resources/merged/cards.json"
ULTRA_BEAST_NAMES = {
    "Buzzwole ex", "Pheromosa", "Kartana", "Blacephalon", "Xurkitree", "Nihilego", "Guzzlord ex",
    "Poipole", "Naganadel", "Stakataka", "Celesteela", "Dawn Wings Necrozma",
    "Dusk Mane Necrozma", "Ultra Necrozma ex"
}


# Utility: Load key-value lookup from DB
def load_lookup_table(cur, table, key_col='name', val_col='id'):
    cur.execute(f"SELECT {val_col}, {key_col} FROM {table};")
    return {row[1]: row[0] for row in cur.fetchall()}


# Clean: Truncate old card-related data
def clear_existing_data(cur):
    cur.execute("TRUNCATE TABLE card CASCADE;")


# Rule ID logic
# Add more rule logic as needed
def get_rule_id(card, rules):
    if card["name"].endswith(" ex"):
        return rules.get("ex")
    return rules.get(card.get("trainerType"))


# Insert one card, return card id
def insert_card(cur, card, lookups):
    subtype_id = (
        lookups["subtypes"].get("Ultra Beast")
        if card["category"] == "Pokemon" and card["name"] in ULTRA_BEAST_NAMES
        else lookups["subtypes"].get(card.get("trainerType"))
    )

    rule_id = get_rule_id(card, lookups["rules"])

    sql = cur.mogrify("""
        INSERT INTO card (
            code, setId, localId, name, supertypeId, illustrator, image,
            rarityId, hp, energyTypeId, evolveFromName, text, stage,
            weaknessId, retreatCost, subtypeId, ruleId
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        card["id"],
        lookups["sets"][card["set"]],
        card["localId"],
        card["name"],
        lookups["supertypes"][card["category"]],
        card.get("illustrator"),
        None,  # image can be handled separately
        lookups["rarities"].get(card["rarity"]),
        card.get("hp"),
        lookups["energy_types"].get(card.get("type")),
        card.get("evolveFrom"),
        card.get("description") or card.get("effect"),
        card.get("stage"),
        lookups["energy_types"].get(card.get("weakness")),
        card.get("retreat"),
        subtype_id,
        rule_id
    ))

    cur.execute(sql)
    return cur.fetchone()[0]


# Booster references
def insert_card_boosters(cur, card_id, card, boosters):
    for booster in card.get("boosters", []):
        match = re.search(r"-([^-]*)$", booster["id"])
        if match:
            booster_code = match.group(1)
            booster_id = boosters.get(booster_code)
            if booster_id:
                cur.execute(
                    "INSERT INTO card_booster (cardId, boosterId) VALUES (%s, %s);",
                    (card_id, booster_id)
                )


# Insert attacks
def insert_attacks(cur, card_id, attacks, energy_codes):
    for attack in attacks:
        cost_str = ''.join(energy_codes[c] for c in attack.get("cost", []) if c in energy_codes)
        cur.execute(
            """
            INSERT INTO attack (cardId, cost, name, effect, damage)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                card_id,
                cost_str,
                attack["name"],
                attack.get("effect"),
                attack.get("damage")
            )
        )


# Insert abilities
def insert_abilities(cur, card_id, abilities):
    for ability in abilities:
        cur.execute(
            "INSERT INTO ability (cardId, name, effect) VALUES (%s, %s, %s);",
            (card_id, ability["name"], ability["effect"])
        )


# Main Builder
def build_cards():
    config = DatabaseConfig()
    with open(CARDS_FILE_PATH, 'r') as file:
        cards = json.load(file)

    with psycopg2.connect(**config.dict()) as conn:
        with conn.cursor() as cur:
            # Load lookup tables
            lookups = {
                # Get (primary key) id for each table using names or codes
                "supertypes": load_lookup_table(cur, "supertype"),
                "sets": load_lookup_table(cur, "set", key_col="code"),
                "rarities": load_lookup_table(cur, "rarity"),
                "energy_types": load_lookup_table(cur, "energy"),
                "energy_codes": load_lookup_table(cur, "energy", val_col="code"),  # For attack cost strings
                "subtypes": load_lookup_table(cur, "subtype"),
                "boosters": load_lookup_table(cur, "booster", key_col="code"),
                "rules": load_lookup_table(cur, "rule")
            }

            clear_existing_data(cur)

            for card in cards:
                card_id = insert_card(cur, card, lookups)
                insert_abilities(cur, card_id, card.get("abilities", []))
                insert_attacks(cur, card_id, card.get("attacks", []), lookups["energy_codes"])
                insert_card_boosters(cur, card_id, card, lookups["boosters"])

        conn.commit()
        print("✅ All cards inserted successfully.")


if __name__ == "__main__":
    build_cards()
