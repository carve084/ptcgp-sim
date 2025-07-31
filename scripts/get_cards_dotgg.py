import requests
import json
import re

from pathlib import Path


OUTPUT_JSON_PATH = Path("../resources/ptcgpocket/cards.json")


def create_typescript_file(filename: str, content: str):
    """
    Creates a new TypeScript file with the specified filename and content.

    Args:
        filename (str): The name of the TypeScript file to create (e.g., "my_module.ts").
        content (str): The TypeScript code to write into the file.
    """
    if not filename.endswith(".ts"):
        filename += ".ts"  # Ensure the file has a .ts extension

    try:
        with open(filename, "w", encoding="utf-8") as ts_file:
            ts_file.write(content)
        print(f"TypeScript file '{filename}' created successfully.")
    except IOError as e:
        print(f"Error creating file '{filename}': {e}")


def fetch_cards(refresh=False):
    """Fetches card data from ptcgpocket. If refresh is True, it will overwrite the existing file."""

    if refresh or not OUTPUT_JSON_PATH.exists():
        # Ensure the output directory exists
        OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Make a GET request to the ptcgpocket API to fetch all cards
        print("Fetching cards from ptcgpocket...")
        response = requests.get("https://api.dotgg.gg/cgfw/getcards?game=pokepocket&mode=indexed")
        response.raise_for_status()  # Raise an error for bad responses

        # Save the cards JSON to a file
        with OUTPUT_JSON_PATH.open('w', encoding='utf-8') as f:
            json.dump(response.json(), f, indent=4)

        print(f"Cards saved to {OUTPUT_JSON_PATH}")

    with OUTPUT_JSON_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def get_tcgdex_cards():
    """Fetches card data from tcgdex/cards.json and returns it as an array of objects."""

    tcgdex_cards_path = Path("../resources/tcgdex/cards.json")
    if not tcgdex_cards_path.exists():
        print(f"TCGdex cards file not found at {tcgdex_cards_path}. Please run get_cards.py first.")
        return []

    with tcgdex_cards_path.open('r', encoding='utf-8') as f:
        return json.load(f)


def get_missing_cards():
    ptcgpocket_cards = fetch_cards(refresh=False)  # Add logic to only fetch if the file does not exist
    tcgdex_cards = get_tcgdex_cards()

    # Compare the two datasets
    ptcgpocket_ids = {card[0] for card in ptcgpocket_cards['data']}
    tcgdex_ids = {card['id'].replace("P-A", "PROMO") for card in tcgdex_cards}
    missing_in_tcgdex = ptcgpocket_ids - tcgdex_ids
    missing_in_ptcgpocket = tcgdex_ids - ptcgpocket_ids
    print(f"Cards in ptcgpocket but missing in tcgdex: {len(missing_in_tcgdex)}")
    print(f"Cards in tcgdex but missing in ptcgpocket: {len(missing_in_ptcgpocket)}")

    if missing_in_tcgdex:
        print("Creating example typescript files for the cards missing in tcgdex...")
        for card_id in missing_in_tcgdex:
            # Get card details from ptcgpocket
            card_details = next((card for card in ptcgpocket_cards['data'] if card[0] == card_id), None)

            # Get the rarity from the get_rarity module
            rarity = {
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
            }.get(card_details[6], "Unknown")

            # Get card type
            if card_details[8] == "Pokemon":
                card_dict = {
                    "set": "Set",
                    "name": {
                        "en": card_details[3]
                    },
                    "illustrator": card_details[22],
                    "category": "Pokemon",
                    "hp": int(card_details[13]),
                    "types": [card_details[7]],
                    "stage": card_details[14].replace(" ", ""),
                    "evolveFrom": {
                        "en": card_details[15]
                    } if card_details[15] else None,
                    "suffix": "EX" if card_details[3].endswith("ex") else None,
                    "abilities": [
                        {
                            "type": "Ability",
                            "name": {
                                "en": ability["info"]
                            },
                            "effect": {
                                "en": ability["effect"].replace("<br />", "\n")
                            }
                        } for ability in card_details[17]
                    ] if card_details[17] and len(card_details[17]) > 0 else None,
                    "attacks": [
                        {
                            "name": {
                                "en": attack["info"]
                            },
                            "cost": [],
                            "damage": 0,
                            "effect": {
                                "en": attack["effect"].replace("<br />", "\n")
                            }
                        } for attack in card_details[16]
                    ] if card_details[16] and len(card_details[16]) > 0 else [],
                    "description": {
                        "en": "" if card_details[18] is None else card_details[18].replace("<br />", "\n")
                    },
                    "weaknesses": [
                        {
                            "type": card_details[19],
                            "value": "+20"
                        }
                    ],
                    "retreat": int(card_details[20]),
                    "rarity": rarity,
                    "boosters": []
                }

                if card_details[15] is None:
                    del card_dict["evolveFrom"]
                if card_dict["suffix"] is None:
                    del card_dict["suffix"]
                if card_details[17] is None or len(card_details[17]) == 0:
                    del card_dict["abilities"]

                card_json = json.dumps(card_dict, indent=4, ensure_ascii=False)
                card_json = re.sub(r'"(\w+)":', r'\1:', card_json).replace('"Set"', 'Set')
                ts_code = f'''import {{ Card }} from "../../../interfaces"
import Set from "../{card_details[5].replace("Promo A", "Promos-A")}"

const card: Card = {card_json}

export default card
'''
            else:
                card_dict = {
                    "set": "Set",
                    "name": {
                        "en": card_details[3]
                    },
                    "illustrator": card_details[22],
                    "category": "Trainer",
                    "effect": {
                        "en": ""
                    },
                    "trainerType": card_details[8],
                    "rarity": rarity,
                    "boosters": []
                }

                card_json = json.dumps(card_dict, indent=4, ensure_ascii=False)
                card_json = re.sub(r'"(\w+)":', r'\1:', card_json).replace('"Set"', 'Set')
                ts_code = f'''import {{ Card }} from "../../../interfaces"
import Set from "../{card_details[5].replace("Promo A", "Promos-A")}"

const card: Card = {card_json}

export default card
'''
            create_typescript_file(f"../resources/tcgdex/missing/{card_details[0]}.ts", ts_code)


if __name__ == '__main__':
    fetch_cards(refresh=True)
