from ptcgp_sim.models import Rule


def load_rules(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM rule")
    rows = cur.fetchall()
    cur.close()
    return [Rule(*row) for row in rows]
