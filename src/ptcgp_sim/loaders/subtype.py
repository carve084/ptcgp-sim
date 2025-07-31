from ptcgp_sim.models import Subtype


def load_subtypes(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM subtype")
    rows = cur.fetchall()
    cur.close()
    return [Subtype(*row) for row in rows]
