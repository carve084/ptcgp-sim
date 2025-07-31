from ptcgp_sim.models import Energy


def load_energies(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, code FROM energy")
    rows = cur.fetchall()
    cur.close()
    return [Energy(*row) for row in rows]
