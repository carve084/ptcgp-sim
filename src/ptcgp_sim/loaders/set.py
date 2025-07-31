from ptcgp_sim.models import Set


def load_sets(conn):
    cur = conn.cursor()
    cur.execute('SELECT id, code, name, cardCountOfficial, cardCountTotal, logo, symbol FROM "set"')
    rows = cur.fetchall()
    cur.close()
    return [Set(*row) for row in rows]
