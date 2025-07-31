import json
from pathlib import Path
from unidecode import unidecode


INPUT_LIMITLESSTCG_PATH = Path("../resources/limitlesstcg/cards.json")
INPUT_PTCGPOCKET_PATH = Path("../resources/ptcgpocket/cards.json")
INPUT_TCDEX_PATH = Path("../resources/tcgdex/cards.json")
OUTPUT_JSON_PATH = Path("../resources/merged/cards.json")
OUTPUT_DIFFERENCES_PATH = Path("../resources/merged/differences.json")


def fetch_limitlesstcg_cards():
    """Fetches card data from limitlesstcg/cards.json and returns it as an array of objects."""

    with INPUT_LIMITLESSTCG_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def fetch_ptcgpocket_cards():
    """Fetches card data from ptcgpocket/cards.json and returns it as an array of objects."""

    with INPUT_PTCGPOCKET_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)['data']


def fetch_tcgdex_cards():
    """Fetches card data from tcgdex/cards.json and returns it as an array of objects."""

    with INPUT_TCDEX_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def cost_string_to_list(cost_string):
    """Converts a cost string to a list of costs."""
    if not cost_string:
        return []
    return [unidecode(cost.strip()) for cost in cost_string.split(',') if cost.strip()]


def transform_attacks(attacks):
    if len(attacks) == 0:
        return []

    cost_map = {
        "G": "Grass",
        "R": "Fire",
        "W": "Water",
        "L": "Lightning",
        "P": "Psychic",
        "F": "Fighting",
        "D": "Darkness",
        "M": "Metal",
        "C": "Colorless"
    }

    transformed = []
    for atk in attacks:
        cost = [cost_map[c] for c in atk["info"]["cost"] if c in cost_map]
        effect = atk.get("effect", "").replace("[", " {").replace("]", "} ")

        attack = {
            "cost": cost,
            "name": atk["info"]["name"].replace("’", "'")
        }

        if effect != "":
            attack["effect"] = effect.replace("−", "-").replace(".(", ". (").replace(" ,", ",").replace(" .", ".")
        if atk["info"]["damage"] != "":
            attack["damage"] = atk["info"]["damage"].replace("×", "x")

        transformed.append(attack)
    return transformed


def transform_abilities(abilities):
    """Transforms abilities from the limitlesstcg format to a more standardized format."""
    if len(abilities) == 0:
        return []

    transformed = []
    for ability in abilities:
        effect = ability.get('effect', '').replace("[", " {").replace("]", "} ").replace(".(", ". (")
        transformed.append({
            "type": "Ability",
            "name": ability['info'],
            "effect": effect
        })
    return transformed


def merge_cards():
    """Merges the card data from limitlesstcg, ptcgpocket, and tcgdex into a single JSON file."""

    limitlesstcg_cards = fetch_limitlesstcg_cards()
    ptcgpocket_cards = fetch_ptcgpocket_cards()
    tcgdex_cards = fetch_tcgdex_cards()

    # Create an array to hold merged cards
    merged_cards = []
    differences = []
    rarity_mapping = {
        "Common": "One Diamond",
        "Uncommon": "Two Diamond",
        "Rare": "Three Diamond",
        "Double Rare": "Four Diamond",
        "Art Rare": "One Star",
        "Super Rare": "Two Star",
        "Special Art Rare": "Two Star",
        "Immersive Rare": "Three Star",
        "Shiny": "One Shiny",
        "Shiny Super Rare": "Two Shiny",
        "Crown Rare": "Crown"
    }

    # First Pass using limitlesstcg cards because they are reliable
    for card in limitlesstcg_cards:
        # Long variable handling
        description = card.get('description', '').replace("’", "'").replace("  ", " ")
        card_data = {
            "id": card['id'],
            "name": card['name'],
            "category": unidecode(card['category']),
            "set": card['set'],
            "localId": card['localId'].zfill(3),
            "illustrator": card.get('illustrator'),
            "rarity": None,  # Rarities are too unreliable from limitlesstcg for now
            "description": description if card.get('description') else None,
            "dex": None,  # Dex will come from ptcgpocket
            "boosters": [],  # Boosters will come from tcgdex
            # Pokemon specific fields
            "type": card.get('type', None),
            "hp": card.get('hp', None),
            "stage": card.get('stage', "").replace(" ", "") if card.get('stage') else None,
            "evolveFrom": card.get('evolveFrom', None),
            "abilities": transform_abilities(card.get('abilities', [])),
            "attacks": transform_attacks(card.get('attacks', [])),
            "weakness": card.get('weakness', None) if card.get('weakness', '') != "none" else None,
            "retreat": card.get('retreat', None),
            # Trainer specific fields
            "trainerType": card.get('trainerType', None),
            "effect": card.get('effect').replace("[ ", "{").replace(" ]", "}") if card.get('effect') else None,
        }
        # Fix P-A-022's hp
        if card_data['id'] == "P-A-022":
            card_data['hp'] = 50
        merged_cards.append(card_data)
    # Second Pass using ptcgpocket cards to fill in missing data
    for card in ptcgpocket_cards:
        card_data = {
            "id": card[0].replace("PROMO", "P-A"),
            "name": card[3].replace("’", "'"),
            "category": "Pokemon" if card[8] == "Pokemon" else "Trainer",
            "set": card[1].replace("PROMO", "P-A"),
            "localId": card[2].zfill(3),
            "illustrator": card[22],
            "rarity": rarity_mapping.get(card[6], None),
            "description": "" if card[18] is None else card[18].replace("<br />", "\n"),
            "dex": card[12],
            "boosters": [],  # Boosters will come from tcgdex
            # Pokemon specific fields
            "type": card[7] if card[8] == "Pokemon" else None,
            "hp": int(card[13]) if card[8] == "Pokemon" else None,
            "stage": card[14].replace(" ", "") if card[8] == "Pokemon" else None,
            "evolveFrom": card[15] if card[8] == "Pokemon" else None,
            "abilities": card[17] if card[8] == "Pokemon" else [],
            "attacks": card[16] if card[8] == "Pokemon" else [],
            "weakness": card[19] if card[8] == "Pokemon" and card[19] != "UNSPECIFIED" else None,
            "retreat": int(card[20]) if card[8] == "Pokemon" else None,
            # Trainer specific fields
            "trainerType": card[8].replace("Pokémon ", "").replace("Fossil", "Item") if card[8] != "Pokemon" else None
        }
        # Find existing card in merged_cards
        existing_card = next((c for c in merged_cards if c['id'] == card_data['id']), None)
        if existing_card:
            # Rarities are most reliable from ptcgpocket for now, so always update it if possible
            # Dex is a string that represents a comma-separated list of dotgg booster codes
            existing_card.update({
                "rarity": card_data['rarity'],
                "dex": card_data['dex'],
            })
            # Compare fields and add a new one if there are differences
            if existing_card.get('name') != card_data['name']:
                existing_card['ptcgpocket_name'] = card_data['name']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_name",
                                    "value": card_data['name']})
            if existing_card.get('category') != card_data['category']:
                existing_card['ptcgpocket_category'] = card_data['category']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_category",
                                    "value": card_data['category']})
            if existing_card.get('set') != card_data['set']:
                existing_card['ptcgpocket_set'] = card_data['set']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_set",
                                    "value": card_data['set']})
            if existing_card.get('localId') != card_data['localId']:
                existing_card['ptcgpocket_localId'] = card_data['localId']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_localId",
                                    "value": card_data['localId']})
            if existing_card.get('illustrator') != card_data['illustrator']:
                existing_card['ptcgpocket_illustrator'] = card_data['illustrator']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_illustrator",
                                    "value": card_data['illustrator']})
            if existing_card.get('type') != card_data['type']:
                existing_card['ptcgpocket_type'] = card_data['type']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_type",
                                    "value": card_data['type']})
            if existing_card.get('hp') != card_data['hp']:
                existing_card['ptcgpocket_hp'] = card_data['hp']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_hp",
                                    "value": card_data['hp']})
            if existing_card.get('stage') != card_data['stage']:
                existing_card['ptcgpocket_stage'] = card_data['stage']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_stage",
                                    "value": card_data['stage']})
            if existing_card.get('evolveFrom') != card_data['evolveFrom']:
                existing_card['ptcgpocket_evolveFrom'] = card_data['evolveFrom']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_evolveFrom",
                                    "value": card_data['evolveFrom']})
            if existing_card.get('weakness') != card_data['weakness']:
                existing_card['ptcgpocket_weakness'] = card_data['weakness']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_weakness",
                                    "value": card_data['weakness']})
            if existing_card.get('retreat') != card_data['retreat']:
                existing_card['ptcgpocket_retreat'] = card_data['retreat']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_retreat",
                                    "value": card_data['retreat']})
            if existing_card.get('trainerType') != card_data['trainerType']:
                existing_card['ptcgpocket_trainerType'] = card_data['trainerType']
                differences.append({"id": card_data['id'], "field": "ptcgpocket_trainerType",
                                    "value": card_data['trainerType']})
    # Third Pass using tcgdex cards to compare data
    for card in tcgdex_cards:
        # Long variable handling
        description = card.get('description', '').replace("’", "'").replace('\n', ' ').replace("  ", " ")
        for attack in card.get('attacks', []):
            if attack.get('damage'):
                attack['damage'] = str(attack['damage']).replace("×", "x")
            if attack.get('effect'):
                attack['effect'] = attack.get('effect').replace("’", "'").replace('−', '-')
        card_data = {
            "id": card['id'],
            "name": card['name'],
            "category": card['category'],
            "set": card['set']['id'],
            "localId": card['localId'],
            "illustrator": card.get('illustrator'),
            "rarity": card.get('rarity', "None"),
            "description": description if card.get('description') else None,
            "dex": None,
            "boosters": card.get('boosters', []),
            # Pokemon specific fields
            "type": card.get('types', [None])[0],
            "hp": card.get('hp', None),
            "stage": card.get('stage', None),
            "evolveFrom": card.get('evolveFrom', None),
            "abilities": card.get('abilities', []),
            "attacks": card.get('attacks', []),
            "weakness": card.get('weaknesses', [{'type': None}])[0]['type'],
            "retreat": card.get('retreat', None),
            # Trainer specific fields
            "trainerType": card.get('trainerType', None),
            "effect": card.get('effect').replace('\n', ' ') if card.get('effect') else None,
        }
        # Find existing card in merged_cards
        existing_card = next((c for c in merged_cards if c['id'] == card_data['id']), None)
        if existing_card:
            existing_card.update({
                'boosters': card_data['boosters'],
            })
            # Compare fields and add a new one if there are differences
            if existing_card.get('name') != card_data['name']:
                existing_card['tcgdex_name'] = card_data['name']
                differences.append({"id": card_data['id'], "field": "tcgdex_name",
                                    "value": existing_card['tcgdex_name']})
            if existing_card.get('category') != card_data['category']:
                existing_card['tcgdex_category'] = card_data['category']
                differences.append({"id": card_data['id'], "field": "tcgdex_category",
                                    "value": existing_card['tcgdex_category']})
            if existing_card.get('set') != card_data['set']:
                existing_card['tcgdex_set'] = card_data['set']
                differences.append({"id": card_data['id'], "field": "tcgdex_set",
                                    "value": existing_card['tcgdex_set']})
            if existing_card.get('localId') != card_data['localId']:
                existing_card['tcgdex_localId'] = card_data['localId']
                differences.append({"id": card_data['id'], "field": "tcgdex_localId",
                                    "value": existing_card['tcgdex_localId']})
            if existing_card.get('illustrator') != card_data['illustrator']:
                existing_card['tcgdex_illustrator'] = card_data['illustrator']
                differences.append({"id": card_data['id'], "field": "tcgdex_illustrator",
                                    "value": existing_card['tcgdex_illustrator']})
            if card_data.get('rarity', "None") != "None" and existing_card.get('rarity') != card_data['rarity']:
                existing_card['tcgdex_rarity'] = card_data['rarity']
                differences.append({"id": card_data['id'], "field": "tcgdex_rarity",
                                    "value": existing_card['tcgdex_rarity']})
            if existing_card.get('description') != card_data['description']:
                existing_card['tcgdex_description'] = card_data['description']
                differences.append({"id": card_data['id'], "field": "tcgdex_description",
                                    "value": existing_card['tcgdex_description']})
            if existing_card.get('type') != card_data['type']:
                existing_card['tcgdex_type'] = card_data['type']
                differences.append({"id": card_data['id'], "field": "tcgdex_type",
                                    "value": existing_card['tcgdex_type']})
            if existing_card.get('hp') != card_data['hp']:
                existing_card['tcgdex_hp'] = card_data['hp']
                differences.append({"id": card_data['id'], "field": "tcgdex_hp",
                                    "value": existing_card['tcgdex_hp']})
            if existing_card.get('stage') != card_data['stage']:
                existing_card['tcgdex_stage'] = card_data['stage']
                differences.append({"id": card_data['id'], "field": "tcgdex_stage",
                                    "value": existing_card['tcgdex_stage']})
            if existing_card.get('evolveFrom') != card_data['evolveFrom']:
                existing_card['tcgdex_evolveFrom'] = card_data['evolveFrom']
                differences.append({"id": card_data['id'], "field": "tcgdex_evolveFrom",
                                    "value": existing_card['tcgdex_evolveFrom']})
            if existing_card.get('abilities') != card_data['abilities']:
                existing_card['tcgdex_abilities'] = card_data['abilities']
                differences.append({"id": card_data['id'], "field": "tcgdex_abilities",
                                    "value": existing_card['tcgdex_abilities']})
            if existing_card.get('attacks') != card_data['attacks']:
                existing_card['tcgdex_attacks'] = card_data['attacks']
                differences.append({"id": card_data['id'], "field": "tcgdex_attacks",
                                    "value": existing_card['tcgdex_attacks']})
            if existing_card.get('weakness') != card_data['weakness']:
                existing_card['tcgdex_weakness'] = card_data['weakness']
                differences.append({"id": card_data['id'], "field": "tcgdex_weakness",
                                    "value": existing_card['tcgdex_weakness']})
            if existing_card.get('retreat') != card_data['retreat']:
                existing_card['tcgdex_retreat'] = card_data['retreat']
                differences.append({"id": card_data['id'], "field": "tcgdex_retreat",
                                    "value": existing_card['tcgdex_retreat']})
            if existing_card.get('trainerType') != card_data['trainerType']:
                existing_card['tcgdex_trainerType'] = card_data['trainerType']
                differences.append({"id": card_data['id'], "field": "tcgdex_trainerType",
                                    "value": existing_card['tcgdex_trainerType']})
            if existing_card.get('effect') != card_data['effect']:
                existing_card['tcgdex_effect'] = card_data['effect']
                differences.append({"id": card_data['id'], "field": "tcgdex_effect",
                                    "value": existing_card['tcgdex_effect']})

    with OUTPUT_JSON_PATH.open('w', encoding='utf-8') as f:
        json.dump(merged_cards, f, indent=4)

    with OUTPUT_DIFFERENCES_PATH.open('w', encoding='utf-8') as f:
        json.dump(differences, f, indent=4)

    print(f"Merged cards saved to {OUTPUT_JSON_PATH}")
    print(f"Differences saved to {OUTPUT_DIFFERENCES_PATH}")
    print(f"Differences found: {len(differences)}")
    return merged_cards


if __name__ == "__main__":
    cards = merge_cards()
    print(f"Total cards merged: {len(cards)}")
