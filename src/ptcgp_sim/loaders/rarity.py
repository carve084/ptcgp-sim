from ptcgp_sim.models import Rarity

def load_rarities(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, symbol, name, dotggName, code FROM rarity")
    rows = cur.fetchall()
    cur.close()
    return [Rarity(*row) for row in rows]
