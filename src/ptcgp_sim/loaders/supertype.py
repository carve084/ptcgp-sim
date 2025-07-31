from ptcgp_sim.models import Supertype


def load_supertypes(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM supertype")
    rows = cur.fetchall()
    cur.close()
    return [Supertype(*row) for row in rows]
