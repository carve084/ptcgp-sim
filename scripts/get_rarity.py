import json


def get_rarity(shinedust_cost) -> str:
    """Determines the rarity based on the Shinedust cost."""
    if shinedust_cost == 50:
        return "One Diamond"
    elif shinedust_cost == 80:
        return "Two Diamond"
    elif shinedust_cost == 360:
        return "Three Diamond"
    elif shinedust_cost == 500:
        return "One Star"
    elif shinedust_cost == 720:
        return "Four Diamond"
    elif shinedust_cost == 1250:
        return "One Shiny"
    elif 1250 < shinedust_cost < 1800:  # Special case for Cyclizar PROMO
        return "One Shiny"
    elif shinedust_cost == 1800:
        return "Two Star"
    elif 1800 < shinedust_cost < 2700:  # Special case for Mewtwo PROMO
        return "Two Shiny"
    elif shinedust_cost == 2700:
        return "Two Shiny"
    elif shinedust_cost == 4000:
        return "Three Star"
    elif shinedust_cost == 20000:
        return "Crown"
    else:
        return "Unknown"


def get_rarity_from_id(card_id):
    with open("../resources/ptcgpocket/cards.json", 'r') as file:
        cards = json.load(file)

    card = next((c for c in cards["data"] if c[0] == card_id), None)
    if card and card[24] and card[24][0] and card[24][0]["flairs"] and card[24][0]["flairs"][0]:
        if card[24][0]["flairs"][0]["name"] == "Special shop ticket":
            return "Two Star"
        demands = card[24][0]["flairs"][0]["demands"]
        # Find the Shinedust cost
        for demand in demands:
            if demand["name"] == "Shinedust":
                return get_rarity(int(demand["amount"]))
    elif card and card[6]:
        # Try this when card[24] does not have what we need
        return {
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
        }.get(card[6], "Unknown")
    else:
        return "Unknown"


def get_promo_rarities():
    with open("../resources/ptcgpocket/cards.json", 'r') as file:
        cards = json.load(file)

    # Only print promo rarities
    for card in cards["data"]:
        if card[1] != "PROMO":
            continue
        # Get demands
        demands = card[24][0]["flairs"][0]["demands"]
        # Find the Shinedust cost
        for demand in demands:
            if demand["name"] == "Shinedust":
                print(f'({card[0]}) {card[3]}: {demand["amount"]} Shinedust - {get_rarity(demand["amount"])}')
                break


if __name__ == "__main__":
    get_promo_rarities()
