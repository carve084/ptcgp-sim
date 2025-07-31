import requests
import json

from pathlib import Path


OUTPUT_JSON_PATH = Path("../resources/tcgdex/cards.json")
TCGDEX_URL = "https://api.tcgdex.net/v2/en"


def fetch_sets():
    """Fetches set data from tcgdex for the Pokemon TCG Pocket series."""

    url = f"{TCGDEX_URL}/series/tcgp"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Return only the sets data
    return response.json()['sets']


def fetch_card_briefs(set_id):
    """Fetches card brief data for a specific set from tcgdex."""

    url = f"{TCGDEX_URL}/sets/{set_id}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Return only the cards data
    return response.json()['cards']


def fetch_card(card_id):
    """Fetches detailed card data for a specific card from tcgdex."""

    url = f"{TCGDEX_URL}/cards/{card_id}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    return response.json()


def fetch_all_cards():
    """ Fetches all set and card data from tcgdex and saves it to JSON files."""

    # Ensure the output directory exists
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Get all card briefs for each set
    print("Fetching sets from tcgdex...")
    sets = fetch_sets()
    card_briefs = []
    for s in sets:
        print(f"Fetching cards for set: {s['name']} ({s['id']})")
        card_briefs += fetch_card_briefs(s['id'])

    cards = []
    count = 0
    card_briefs_length = len(card_briefs)
    for card_brief in card_briefs:
        count += 1
        print(f"Fetching card ({count}/{card_briefs_length}): {card_brief['name']} (ID: {card_brief['id']})")
        cards.append(fetch_card(card_brief['id']))

    with OUTPUT_JSON_PATH.open('w', encoding='utf-8') as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)

    print(f"Cards saved to {OUTPUT_JSON_PATH}")


if __name__ == '__main__':
    fetch_all_cards()
