from ptcgp_sim.models import CardBooster


def load_card_boosters(conn):
    cur = conn.cursor()
    cur.execute("SELECT cardId, boosterId FROM card_booster")
    rows = cur.fetchall()
    cur.close()
    return [CardBooster(*row) for row in rows]
