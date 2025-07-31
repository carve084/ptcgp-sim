import json
import psycopg2
import re

from unidecode import unidecode

from ptcgp_sim.db import DatabaseConfig

# This script should update the card, card_subtype, card_pack, attack, and ability tables from cards.json
# You can update cards.json via get_cards_dotgg.py


def build_cards():
    # Connect and create cursor
    config = DatabaseConfig()
    conn = psycopg2.connect(host=config.host, dbname=config.dbname, user=config.user, password=config.password,
                            port=config.port)
    cur = conn.cursor()

    with open("../resources/ptcgpocket/cards.json", 'r') as file:
        cards = json.load(file)

    # Truncate old data
    cur.execute("TRUNCATE TABLE card CASCADE;")

    # Get Sets
    sets = {}
    cur.execute("SELECT id, code FROM set;")
    for s in cur.fetchall():
        sets[s[1]] = s[0]

    # Get rarities
    rarities = {}
    cur.execute("SELECT id, name FROM rarity;")
    for rarity in cur.fetchall():
        rarities[rarity[1]] = rarity[0]

    # Get types
    types = {None: None, "": None, "UNSPECIFIED": None}
    type_codes = {}
    cur.execute("SELECT id, name, code FROM type;")
    for t in cur.fetchall():
        types[t[1]] = t[0]
        type_codes[t[2]] = t[0]

    # Get subtypes
    subtypes = {}
    cur.execute("SELECT id, name FROM subtype;")
    for subtype in cur.fetchall():
        subtypes[subtype[1]] = subtype[0]

    # List of ultra beasts as of 2025-06-13
    ultra_beast_names = ["Buzzwole ex", "Pheromosa", "Kartana", "Blacephalon", "Xurkitree", "Nihilego", "Guzzlord ex",
                         "Poipole", "Naganadel", "Stakataka", "Celesteela", "Dawn Wings Necrozma", "Dusk Mane Necrozma",
                         "Ultra Necrozma ex"]

    # Get packs
    packs = {}
    cur.execute("SELECT id, dotggCode FROM pack;")
    for pack in cur.fetchall():
        packs[pack[1]] = pack[0]

    for card in cards["data"]:
        # Unidecode card[8] to remove e accent from Pokemon
        card[8] = unidecode(card[8])

        # Get supertypeId
        if card[8] == "Pokemon":
            supertype_id = 1
        else:  # Trainer
            supertype_id = 2

        # Get weakness
        if card[19] is None or len(card[19]) == 0:
            weakness = None
        else:
            weakness = types[card[19]]

        # Insert card
        sql = cur.mogrify("""
            INSERT INTO card (code, setId, number, name, rarityId, typeId, supertypeId, slug, dex, hp, stage,
                preStageName, text, weaknessId, retreatCost, rule, illustrator)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (card[0], sets[card[1]], card[2], card[3], rarities[card[6]], types[card[7]], supertype_id, card[9],
              card[12], card[13], card[14], card[15], card[18], weakness, card[20], card[21], card[22]))
        cur.execute(sql)
        card_id = cur.fetchone()

        # Update card_subtype
        if card[8] == "Pokemon":
            subtype_id = subtypes[card[14]]
        else:
            subtype_id = subtypes[card[8]]
        sql = cur.mogrify("INSERT INTO card_subtype (cardId, subtypeId) VALUES (%s, %s);", (card_id, subtype_id))
        cur.execute(sql)

        # Add Ultra Beast subtype
        if card[3] in ultra_beast_names:
            sql = cur.mogrify("""
                INSERT INTO card_subtype (cardId, subtypeId) VALUES (%s, %s);
            """, (card_id, subtypes["Ultra Beast"]))
            cur.execute(sql)

        # Update card_pack
        if card[12] is not None and len(card[12]) > 0:
            for pack in card[12].split(","):
                if pack in packs:
                    sql = cur.mogrify("""
                        INSERT INTO card_pack (cardId, packId, cardNumber) VALUES (%s, %s, %s);
                    """, (card_id, packs[pack], card[2]))
                    cur.execute(sql)

        # Update attack
        if card[16] is not None:
            for attack in card[16]:
                # Parse for cost
                type_cost_string = re.search(r"{([^}]+)}", attack["info"]).group(1)
                type_costs = []
                for char in type_cost_string:
                    type_costs.append(type_codes[char])
                sql = cur.mogrify("""
                    INSERT INTO attack (cardId, typeCosts, info, effect)
                    VALUES (%s, %s, %s, %s);
                """, (card_id, type_costs, attack["info"], attack["effect"]))
                cur.execute(sql)

        # Update ability
        if card[17] is not None and len(card[17]) > 0:
            for ability in card[17]:
                sql = cur.mogrify("INSERT INTO ability (cardId, name, text) VALUES (%s, %s, %s);",
                                  (card_id, ability["info"], ability["effect"]))
                cur.execute(sql)

    # Commit changes
    conn.commit()

    # Close database
    cur.close()
    conn.close()


if __name__ == "__main__":
    build_cards()
