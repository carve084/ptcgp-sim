import requests
import json

from pathlib import Path


OUTPUT_GAME_PATH = Path("../resources/pokemon-zone/game.json")
OUTPUT_CARDS_PATH = Path("../resources/pokemon-zone/cards.json")
POKEMON_ZONE_URL = "https://www.pokemon-zone.com/api"

# Returns game data including cards, cardSkins, packs, and other metadata
POKEMON_ZONE_GAME_DATA_URL = f"{POKEMON_ZONE_URL}/game/game-data/"

# Returns up to 24 cards with detailed data, or lists of cards with limited data depending on options
# Options include:
# - ?page=<pageNumber>
#       1, 2, 3, etc.
#       Returns 24 cards of the specified page with detailed data.
# - ?series=<expansionId>
#       PROMO-A, A1, A1a, A2, A2a, A2b, A3, A3a, A3b, etc.
#       Returns 24 cards of the specified series with detailed data.
# - search/
#       Returns all cards with limited data
# - search/?series=<expansionId>
#       PROMO-A, A1, A1a, A2, A2a, A2b, A3, A3a, A3b, etc.
#       Returns all cards of the specified series with limited data.
# - search/data/
#       Returns a list of search options. Use this if necessary to find other options.
POKEMON_ZONE_CARDS_URL = f"{POKEMON_ZONE_URL}/cards/"


def fetch(url=POKEMON_ZONE_CARDS_URL):
    """Fetches from Pokemon Zone."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


def save_to_json(data, output_path):
    """Saves data to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {output_path}")


def fetch_all_cards():
    # Ensure the output directory exists
    OUTPUT_GAME_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_CARDS_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Fetching game data from Pokemon Zone...")
    save_to_json(fetch(url=POKEMON_ZONE_GAME_DATA_URL).get('data', {}), OUTPUT_GAME_PATH)

    print("Fetching cards from Pokemon Zone...")
    result = fetch(url=POKEMON_ZONE_CARDS_URL)
    count = result.get('count', 0)
    next_result = result.get('next', None)
    cards = result.get('results', [])
    while next_result:
        print(f"Fetching more cards... {len(cards)}/{count} cards fetched so far.")
        result = fetch(url=next_result)
        next_result = result.get('next', None)
        cards.extend(result.get('results', []))

    print(f"Total cards fetched: {count}")
    save_to_json(cards, OUTPUT_CARDS_PATH)


if __name__ == "__main__":
    fetch_all_cards()
