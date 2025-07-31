import asyncio
import json

from tcgdexsdk import TCGdex, Query
from pathlib import Path


OUTPUT_JSON_PATH = Path("../resources/tcgdex/cards.json")


# This file will make a get request to tcgdex's api and save all the card data that they have to cards.json
# This file is currently not used because tcgdexsdk for Python gives reduced functionality over the JavaScript version.
# See get_cards.py for the current implementation.
def serialize_card(card):
    """Return a serializable dictionary version of a TCGdex card."""
    attacks = []
    weaknesses = []

    if hasattr(card, "attacks") and card.attacks is not None:
        for attack in card.attacks:
            attacks.append({
                "name": attack.name,
                "cost": attack.cost,
                "damage": attack.damage,
                "effect": getattr(attack, "effect", None)
            })
    if hasattr(card, "weaknesses") and card.weaknesses is not None:
        for weakness in card.weaknesses:
            weaknesses.append({
                "type": weakness.type,
                "value": weakness.value
            })
    return {
        "id": card.id,
        "localId": card.localId,
        "name": card.name,
        "image": getattr(card, "image", None),
        "category": card.category,
        "illustrator": getattr(card, "illustrator", None),
        "rarity": getattr(card, "rarity", None),
        # "boosters": array of boosters[].id and boosters[].name
        "set": {
            "id": card.set.id,
            "name": card.set.name,
            "logo": getattr(card.set, "logo", None),
            "symbol": getattr(card.set, "symbol", None)
        },
        #  Pokemon specific fields
        "hp": getattr(card, "hp", None),
        "types": getattr(card, "types", []),
        "evolveFrom": getattr(card, "evolveFrom", None),
        "description": getattr(card, "description", None),
        "stage": getattr(card, "stage", None),
        "suffix": getattr(card, "suffix", None),
        "attacks": attacks,
        "weaknesses": weaknesses,
        "retreat": getattr(card, "retreat", None),
        #  Trainer specific fields
        "effect": getattr(card, "effect", None),
        "trainerType": getattr(card, "trainerType", None)
    }


async def main():
    tcgdex = TCGdex("en")

    # Fetch the series and sets
    serie = await tcgdex.serie.get("tcgp")
    sets = serie.sets

    print(f"Found {len(sets)} sets in series '{serie.name}'.")

    # Asynchronously get all card briefs for each set
    card_briefs_lists = await asyncio.gather(*[
        tcgdex.card.list(Query().equal("set.id", s.id))
        for s in sets
    ])

    print(f"Found {sum(len(cards) for cards in card_briefs_lists)} cards across all sets.")

    # Flatten the list of lists
    card_briefs = [card for sublist in card_briefs_lists for card in sublist]
    card_briefs_length = len(card_briefs)

    print(f"Total card briefs fetched: {card_briefs_length}")

    # Fetch full card data with progress printing
    cards = []
    count = 0

    for cb in card_briefs:
        count += 1
        print(f"Fetching card ({count}/{card_briefs_length}): {cb.name} (ID: {cb.id})")
        card = await tcgdex.card.get(cb.id)
        cards.append(serialize_card(card))

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)

    # Now `cards` is a list of all full card objects
    return cards


if __name__ == "__main__":
    all_cards = asyncio.run(main())
