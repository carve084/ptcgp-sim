import json
import psycopg2
import re

from pathlib import Path
from ptcgp_sim.db import DatabaseConfig


# This script should update the set and pack tables from cards.json
# You can update sets.json via get_sets.py


SETS_FILE_PATH = Path("../resources/tcgdex/sets.json")


def get_dotgg_code(booster_code):
    """
    This function returns the dotgg code for a booster.
    Dotgg codes will need to be added manually here over time.
    Booster_code is based on the booster ids from tcgdex.net, and I added codes for boosters that are missing for now.
    """
    if booster_code.startswith('vol'):
        return booster_code.replace('vol', 'PROMOA')
    return {
        'mewtwo': 'A1_1',
        'charizard': 'A1_2',
        'pikachu': 'A1_3',
        'mew': 'A1a',
        'dialga': 'A2_1',
        'palkia': 'A2_2',
        'arceus': 'A2a',
        'shining': 'A2b',
        'solgaleo': 'A3_1',
        'lunala': 'A3_2',
        'extradimensional': 'A3a',
        'eevee': 'A3b'
    }.get(booster_code, '')


def insert_set(cur, s):
    sql = cur.mogrify("""
        INSERT INTO set (code, name, cardCountOfficial, cardCountTotal, logo, symbol)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (s['id'], s['name'], s['cardCount']['official'], s['cardCount']['total'], s.get('logo', None),
          s.get('symbol', None)))
    cur.execute(sql)
    return cur.fetchone()[0]


def insert_boosters(cur, boosters, set_id):
    for booster in boosters:
        match = re.search(r"-([^-]*)$", booster['id'])
        if match:
            booster_code = match.group(1)
            sql = cur.mogrify("""
                INSERT INTO booster (name, code, dotggCode, setId)
                VALUES (%s, %s, %s, %s);
            """, (booster['name'], booster_code, get_dotgg_code(booster_code), set_id))
            cur.execute(sql)


def build_sets():
    config = DatabaseConfig()

    with psycopg2.connect(**config.dict()) as conn:
        with conn.cursor() as cur:
            with open(SETS_FILE_PATH, 'r', encoding='utf-8') as f:
                sets = json.load(f)

            cur.execute("TRUNCATE TABLE set CASCADE;")
            cur.execute("TRUNCATE TABLE booster CASCADE;")

            for s in sets:
                set_id = insert_set(cur, s)
                if 'boosters' in s:
                    insert_boosters(cur, s['boosters'], set_id)

            print("✅ Sets and boosters imported successfully.")


if __name__ == "__main__":
    try:
        build_sets()
    except Exception as e:
        print(f"❌ Error building sets: {e}")
