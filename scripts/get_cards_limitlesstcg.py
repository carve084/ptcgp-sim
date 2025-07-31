import requests
import re
import json
import time

import get_rarity

from bs4 import BeautifulSoup
from pathlib import Path
from unidecode import unidecode


OUTPUT_JSON_PATH = Path("../resources/limitlesstcg/cards.json")
OUTPUT_JSON_TCGDEX_MISSING_DIR = Path("../resources/tcgdex/missing")


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


def parse_card_details(set_code: str, card_id: str) -> dict:
    url = f"https://pocket.limitlesstcg.com/cards/{set_code}/{card_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch card HTML (status {response.status_code}): {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    card = {
        "id": f"{set_code}-{card_id.zfill(3)}",  # Ensure card ID is zero-padded to 3 digits
        "set": set_code,
        "localId": card_id,
    }

    # First, get the card category (supertype)
    category = "Unknown"
    type_p = soup.find("p", class_="card-text-type")
    if type_p:
        # noinspection PyArgumentList
        type_text = type_p.get_text(separator=" ", strip=True)
        # Split like "Pokémon - Stage 2 - Evolves from Luxio" or "Trainer - Tool"
        parts = type_text.split(" - ")
        category = unidecode(parts[0].strip()) if len(parts) > 0 else None
        card["category"] = category

    if category == "Pokemon":
        # --- Name, Type, HP ---
        title_p = soup.find("p", class_="card-text-title")
        if title_p:
            name_tag = title_p.find("span", class_="card-text-name")
            card["name"] = name_tag.get_text(strip=True) if name_tag else None

            # Remove name tag content to parse rest of string cleanly
            for tag in name_tag.find_all():
                tag.decompose()

            # noinspection PyArgumentList
            remaining_text = title_p.get_text(" ", strip=True)
            # Example: "- Lightning - 130 HP"
            type_match = re.search(r"-\s*(.*?)\s*-\s*(\d+)\s*HP", remaining_text)
            if type_match:
                card["type"] = type_match.group(1).strip()
                card["hp"] = int(type_match.group(2))
            else:
                card["types"] = None
                card["hp"] = 0

        # --- Stage, Evolves From ---
        type_p = soup.find("p", class_="card-text-type")
        if type_p:
            # noinspection PyArgumentList
            type_text = type_p.get_text(" ", strip=True)
            # Split like "Pokémon - Stage 2 - Evolves from Luxio"
            parts = type_text.split(" - ")

            card["stage"] = parts[1].strip() if len(parts) > 1 and "Stage" in parts[1] else "Basic"

            # Evolves from may be in <a> tag
            evolve_tag = type_p.find("a")
            card["evolveFrom"] = evolve_tag.get_text(strip=True) if evolve_tag else None

        # --- Abilities ---
        card["abilities"] = []
        for ability_div in soup.find_all("div", class_="card-text-ability"):
            info = ability_div.find("p", class_="card-text-ability-info")
            effect = ability_div.find("p", class_="card-text-ability-effect")
            ability_name = info.get_text(strip=True).replace("Ability:", "").strip() if info else ""
            card["abilities"].append({
                "info": ability_name,
                "effect": effect.get_text(strip=True) if effect else ""
            })

        # --- Attacks ---
        card["attacks"] = []
        for attack_div in soup.find_all("div", class_="card-text-attack"):
            info = attack_div.find("p", class_="card-text-attack-info")
            effect = attack_div.find("p", class_="card-text-attack-effect")

            cost = ''.join(span.get_text(strip=True) for span in info.find_all("span", class_="ptcg-symbol"))
            full_info = info.get_text(strip=True).replace(cost, '', 1).strip()

            tokens = full_info.split()
            if tokens and re.search(r'\d', tokens[-1]):
                damage = tokens[-1]
                name = ' '.join(tokens[:-1])
            else:
                damage = ''
                name = full_info

            card["attacks"].append({
                "info": {
                    "cost": cost,
                    "name": name,
                    "damage": damage
                },
                "effect": effect.get_text(strip=True) if effect else ""
            })

        # --- Weakness & Retreat ---
        wrr_p = soup.find("p", class_="card-text-wrr")
        if wrr_p:
            # noinspection PyArgumentList
            text = wrr_p.get_text(separator="|", strip=True)
            parts = text.split("|")
            for part in parts:
                if part.startswith("Weakness:"):
                    card["weakness"] = part.replace("Weakness:", "").strip()
                elif part.startswith("Retreat:"):
                    retreat_val = part.replace("Retreat:", "").strip()
                    try:
                        card["retreat"] = int(retreat_val)
                    except ValueError:
                        card["retreat"] = 0
    else:
        # For Trainer cards, handle differently
        # --- Name ---
        title_p = soup.find("p", class_="card-text-title")
        if title_p:
            name_tag = title_p.find("span", class_="card-text-name")
            card["name"] = name_tag.get_text(strip=True) if name_tag else None

        # --- TrainerType ---
        type_p = soup.find("p", class_="card-text-type")
        if type_p:
            # noinspection PyArgumentList
            type_text = type_p.get_text(" ", strip=True)
            # Split like "Trainer - Tool"
            parts = type_text.split(" - ")
            card["trainerType"] = parts[1].strip() if len(parts) > 1 else "Unknown"

        # --- Effect ---
        sections = soup.find_all("div", class_="card-text-section")
        if len(sections) > 2:
            # noinspection PyArgumentList
            card["effect"] = sections[1].get_text(separator=" ", strip=True)

    # --- Illustrator ---
    artist_div = soup.find("div", class_="card-text-section card-text-artist")
    if artist_div:
        artist_tag = artist_div.find("a")
        card["illustrator"] = artist_tag.get_text(strip=True) if artist_tag else None

    # --- Description / Flavor Text ---
    flavor_div = soup.find("div", class_="card-text-section card-text-flavor")
    if flavor_div:
        card["description"] = flavor_div.get_text(strip=True)

    # --- Rarity ---
    # Less reliable because:
    # 1. Shinies have the same code as stars
    # 2. Promos do not have rarities and there is no way to derive it from only limitlesstcg
    # rarity_div = soup.find("div", class_="prints-current-details")
    # rarity = "Unknown"

    # if rarity_div:
    #     span_elements = rarity_div.find_all("span")
    #     if len(span_elements) > 1:
    #         text = span_elements[1].get_text(strip=True)
    #         parts = [p.strip() for p in text.split("·")]
    #         if len(parts) > 1:
    #             rarity = parts[1]

    # print(f"({card['id']}) {card['name']} limitlesstcg rarity: {rarity}")

    # Override rarity for now
    rarity = get_rarity.get_rarity_from_id(card["id"].replace("P-A", "PROMO"))

    # Debug
    if rarity is None or rarity == "Unknown":
        print(f"({card['id'].replace('P-A', 'PROMO')}) {card['name']} ptcgpocket rarity: {rarity}")

    card["rarity"] = rarity

    return card


def fetch_card_list():
    url = "https://pocket.limitlesstcg.com/api/dm/search"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch card list: {response.status_code}")

    return response.json()


def build_all_cards(delay=0):  # delay is in seconds. 0.5 is a good value
    cards = fetch_card_list()
    parsed_cards = []

    for i, card in enumerate(cards, start=1):
        set_code = card.get("set")
        card_id = card.get("number")

        print(f"Fetching card {i}/{len(cards)}: {set_code} {card_id} - {card.get('name')}")
        try:
            card_data = parse_card_details(set_code, card_id)
            parsed_cards.append(card_data)
        except Exception as e:
            print(f"❌ Failed to parse card {set_code}/{card_id}: {e}")

        # Be polite to the server
        if delay > 0:
            time.sleep(delay)

    # Save to JSON
    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(parsed_cards, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(parsed_cards)} cards to {OUTPUT_JSON_PATH}")


def build_cards(cards, delay=0):  # delay is in seconds. 0.5 is a good value
    parsed_cards = []

    for i, card in enumerate(cards, start=1):
        set_code = card.get("set")
        card_id = card.get("number")

        print(f"Fetching card {i}/{len(cards)}: {set_code} {card_id} - {card.get('name')}")
        try:
            card_data = parse_card_details(set_code, card_id)
            parsed_cards.append(card_data)
        except Exception as e:
            print(f"❌ Failed to parse card {set_code}/{card_id}: {e}")

        # Be polite to the server
        if delay > 0:
            time.sleep(delay)

    # Update JSON
    with OUTPUT_JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of objects.")

    # Replace the object by ID
    for card in parsed_cards:
        # Find and update the object in the existing data
        updated = False
        for i, obj in enumerate(data):
            if obj["id"] == card["id"]:
                data[i] = card
                updated = True
                break

        if not updated:
            raise ValueError(f"No object with id {card['id']} found.")
        else:
            print(f"✅ Card ({card['id']}) {card['name']} updated successfully.")

    # Save updated data
    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_limitlesstcg_cards():
    """Fetches card data from tcgdex/cards.json and returns it as an array of objects."""

    if not OUTPUT_JSON_PATH.exists():
        print(f"LimitlessTCG cards file not found at {OUTPUT_JSON_PATH}. Please run build_all_cards() first.")
        return []

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
            "name": {
                "en": atk["info"]["name"].replace("’", "'")
            }
        }

        if effect != "":
            attack["effect"] = {
                "en": effect.replace("−", "-").replace(".(", ". (").replace(" ,", ",").replace(" .", ".")
            }
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
            "name": {
                "en": ability['info']
            },
            "effect": {
                "en": effect
            }
        })
    return transformed


def get_missing_cards():
    limitlesstcg_cards = get_limitlesstcg_cards()  # Add logic to only fetch if the file does not exist
    tcgdex_cards = get_tcgdex_cards()

    # Compare the two datasets
    limitlesstcg_ids = {card['id'] for card in limitlesstcg_cards}
    tcgdex_ids = {card['id'] for card in tcgdex_cards}
    missing_in_tcgdex = limitlesstcg_ids - tcgdex_ids
    missing_in_ptcgpocket = tcgdex_ids - limitlesstcg_ids
    print(f"Cards in ptcgpocket but missing in tcgdex: {len(missing_in_tcgdex)}")
    print(f"Cards in tcgdex but missing in ptcgpocket: {len(missing_in_ptcgpocket)}")

    if missing_in_tcgdex:
        print("Creating example typescript files for the cards missing in tcgdex...")
        for card_id in missing_in_tcgdex:
            # Get card details from limitlesstcg
            card_details = next((card for card in limitlesstcg_cards if card['id'] == card_id), None)

            # Get card type
            if card_details['category'] == "Pokemon":
                card_dict = {
                    "set": "Set",
                    "name": {
                        "en": card_details["name"]
                    },
                    "illustrator": card_details["illustrator"],
                    "category": "Pokemon",
                    "hp": int(card_details["hp"]),
                    "types": [card_details["type"]],
                    "stage": card_details["stage"].replace(" ", ""),
                    "evolveFrom": {
                        "en": card_details["evolveFrom"]
                    } if card_details["evolveFrom"] else None,
                    "suffix": "EX" if card_details["name"].endswith("ex") else None,
                    "abilities": transform_abilities(card_details.get("abilities", [])),
                    "attacks": transform_attacks(card_details.get("attacks", [])),
                    "description": {
                        "en": card_details.get("description", None)
                    },
                    "weaknesses": [
                        {
                            "type": card_details["weakness"],
                            "value": "+20"
                        }
                    ],
                    "retreat": int(card_details["retreat"]),
                    "rarity": card_details["rarity"],
                    "boosters": []
                }

                if card_details["evolveFrom"] is None:
                    del card_dict["evolveFrom"]
                if card_dict["suffix"] is None:
                    del card_dict["suffix"]
                if card_details["abilities"] is None or len(card_details["abilities"]) == 0:
                    del card_dict["abilities"]

                card_json = json.dumps(card_dict, indent=4, ensure_ascii=False)
                card_json = re.sub(r'"(\w+)":', r'\1:', card_json).replace('"Set"', 'Set')
                ts_code = f'''import {{ Card }} from "../../../interfaces"
import Set from "../{card_details["set"].replace("P-A", "Promos-A")}"

const card: Card = {card_json}

export default card
'''
            else:
                card_dict = {
                    "set": "Set",
                    "name": {
                        "en": card_details["name"]
                    },
                    "illustrator": card_details["illustrator"],
                    "category": "Trainer",
                    "effect": {
                        "en": card_details["effect"]
                    },
                    "trainerType": card_details["trainerType"],
                    "rarity": card_details["rarity"],
                    "boosters": []
                }

                card_json = json.dumps(card_dict, indent=4, ensure_ascii=False)
                card_json = re.sub(r'"(\w+)":', r'\1:', card_json).replace('"Set"', 'Set')
                ts_code = f'''import {{ Card }} from "../../../interfaces"
import Set from "../{card_details["set"]}"

const card: Card = {card_json}

export default card
'''
            output_path = f"../resources/tcgdex/missing/{card_details['set']}/{card_details['localId'].zfill(3)}.ts"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            create_typescript_file(output_path, ts_code)


if __name__ == "__main__":
    get_missing_cards()
