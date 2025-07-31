from ptcgp_sim.models import Booster


def load_boosters(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, code, dotggCode, setId FROM booster")
    rows = cur.fetchall()
    cur.close()
    return [Booster(*row) for row in rows]
