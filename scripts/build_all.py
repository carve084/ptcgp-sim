import build_tables
import build_sets
import build_cards


def build_all():
    print("Building all tables...")
    build_tables.build_tables()
    print("Building sets and packs...")
    build_sets.build_sets()
    # print("Building cards, card_subtypes, card_packs, attacks, and abilities...")
    # build_cards.build_cards()


if __name__ == "__main__":
    build_all()
