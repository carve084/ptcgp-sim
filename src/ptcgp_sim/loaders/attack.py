from ptcgp_sim.models import Attack


def load_attacks(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, cardId, cost, name, effect, damage FROM attack")
    rows = cur.fetchall()
    cur.close()
    return [Attack(*row) for row in rows]


def load_attacks_for_card(conn, card_id):
    cur = conn.cursor()
    cur.execute("SELECT id, cardId, cost, name, effect, damage FROM attack WHERE cardId = %s", (card_id,))
    rows = cur.fetchall()
    cur.close()
    return [Attack(*row) for row in rows]
