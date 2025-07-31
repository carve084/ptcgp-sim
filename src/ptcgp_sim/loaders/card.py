from collections import defaultdict
from ptcgp_sim.models.card import CardData
from ptcgp_sim.models.ability import Ability
from ptcgp_sim.models.attack import Attack
from ptcgp_sim.loaders.common import (
    load_sets, load_supertypes, load_rarities, load_rules,
    load_energies, load_subtypes
)


def load_lookups(conn) -> dict:
    return {
        "sets": {s.id: s for s in load_sets(conn)},
        "supertypes": {s.id: s for s in load_supertypes(conn)},
        "rarities": {r.id: r for r in load_rarities(conn)},
        "rules": {r.id: r for r in load_rules(conn)},
        "energies": {e.id: e for e in load_energies(conn)},
        "subtypes": {s.id: s for s in load_subtypes(conn)}
    }


def load_cards(conn) -> list[CardData]:
    # 1. Load all the simple lookup tables once.
    lookups = load_lookups(conn)

    # 2. Fetch all cards in a single query.
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, code, setId, localId, name, supertypeId, illustrator, image,
                   rarityId, hp, energyTypeId, evolveFromName, text, stage,
                   weaknessId, retreatCost, subtypeId, ruleId
            FROM card;
        """)
        rows = cur.fetchall()

    cards_by_id = {}
    card_ids = []
    for row in rows:
        (
            card_id, code, set_id, local_id, name, supertype_id, illustrator, image,
            rarity_id, hp, energy_type_id, evolve_from, text, stage,
            weakness_id, retreat_cost, subtype_id, rule_id
        ) = row

        card_ids.append(card_id)

        card = CardData(
            id=card_id,
            code=code,
            set=lookups["sets"].get(set_id),
            local_id=local_id,
            name=name,
            supertype=lookups["supertypes"].get(supertype_id),
            illustrator=illustrator,
            image=image,
            rarity=lookups["rarities"].get(rarity_id),
            hp=hp,
            energy_type=lookups["energies"].get(energy_type_id),
            evolve_from=evolve_from,
            text=text,
            stage=stage,
            weakness=lookups["energies"].get(weakness_id),
            retreat_cost=retreat_cost,
            subtype=lookups["subtypes"].get(subtype_id),
            rule=lookups["rules"].get(rule_id),

            abilities=[],
            attacks=[]
        )
        cards_by_id[card_id] = card

    # 3. If there are no cards, we're done.
    if not card_ids:
        return []

    # 4. Fetch ALL abilities for ALL cards in one go.
    abilities_by_card_id = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute("SELECT id, cardId, name, effect FROM ability WHERE cardId = ANY(%s);", (card_ids,))
        for row in cur.fetchall():
            (ability_id, ability_card_id, ability_name, ability_effect) = row
            ability = Ability(*row)
            abilities_by_card_id[ability_card_id].append(ability)

    # 5. Fetch ALL attacks for ALL cards in one go.
    attacks_by_card_id = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute("SELECT id, cardId, cost, name, effect, damage FROM attack WHERE cardId = ANY(%s);", (card_ids,))
        for row in cur.fetchall():
            (attack_id, attack_card_id, attack_cost, attack_name, attack_effect, attack_damage) = row
            attack = Attack(*row)
            attacks_by_card_id[attack_card_id].append(attack)

    # 6. "Stitch" the data together in Python (this is extremely fast).
    for card_id, card in cards_by_id.items():
        card.abilities = abilities_by_card_id.get(card_id, [])
        card.attacks = attacks_by_card_id.get(card_id, [])

    return list(cards_by_id.values())
