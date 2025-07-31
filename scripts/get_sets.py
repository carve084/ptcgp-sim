import requests
import json

from pathlib import Path


OUTPUT_JSON_PATH = Path("../resources/tcgdex/sets.json")
TCGDEX_URL = "https://api.tcgdex.net/v2/en"


def fetch_set_briefs():
    """Fetches set data from tcgdex for the Pokemon TCG Pocket series."""

    url = f"{TCGDEX_URL}/series/tcgp"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Return only the sets data
    return response.json()['sets']


def fetch_set(set_id):
    """Fetches detailed set data for a specific set from tcgdex."""

    url = f"{TCGDEX_URL}/sets/{set_id}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    return response.json()


def fetch_all_sets():
    # Ensure the output directory exists
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Get all sets
    print("Fetching sets from tcgdex...")
    set_briefs = fetch_set_briefs()

    # Get set data
    sets = []
    count = 0
    set_briefs_length = len(set_briefs)
    for set_brief in set_briefs:
        count += 1
        print(f"Fetching set {count}/{set_briefs_length}: {set_brief['name']} ({set_brief['id']})")
        sets.append(fetch_set(set_brief['id']))

    # Save the sets data to JSON
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as file:
        json.dump(sets, file, indent=4, ensure_ascii=False)

    print(f"Sets data saved to {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    fetch_all_sets()
