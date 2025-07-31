from ptcgp_sim.models import Ability


def load_abilities(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, cardId, name, effect FROM ability;")
    rows = cur.fetchall()
    cur.close()
    return [Ability(*row) for row in rows]


def load_abilities_for_card(conn, card_id):
    cur = conn.cursor()
    cur.execute("SELECT id, cardId, name, effect FROM ability WHERE cardId = %s;", (card_id,))
    rows = cur.fetchall()
    cur.close()
    return [Ability(*row) for row in rows]
