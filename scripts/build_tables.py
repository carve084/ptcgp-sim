import psycopg2

from pathlib import Path
from ptcgp_sim.db import DatabaseConfig


# This script recreates the database schema from scratch using raw SQL files.
# It should be used during local development or initial database setup.
#
# To use this script:
# 1. Install PostgreSQL and create a database (e.g., "ptcgp").
# 2. pip install psycopg2
# 3. Update `config.py` with your local database credentials.
# 4. Ensure the `../sql` directory contains valid table definition files.


def execute_sql_files(cursor, connection, table_names, table_dir):
    """
    Executes each SQL file in `table_names` from the specified `table_dir`.
    Rolls back and re-raises the error if any execution fails.
    """
    for table in table_names:
        path = table_dir / f"{table}.sql"
        try:
            sql = path.read_text()
            cursor.execute(sql)
        except Exception as e:
            print(f"❌ Error executing {path.name}: {e}")
            connection.rollback()
            raise


def build_tables():
    config = DatabaseConfig()

    try:
        with psycopg2.connect(**config.dict()) as conn:
            with conn.cursor() as cur:
                table_dir = Path("../sql")

                # Table groups are ordered by dependency depth.
                # Group 1: Tables with no foreign key constraints.
                # Group 2: Tables that depend on Group 1.
                # Group 3: Tables that depend on Group 2.
                table_groups = [
                    [
                        "energy",
                        "rarity",
                        "rule",
                        "set",
                        "subtype",
                        "supertype"
                    ],
                    [
                        "booster",      # Foreign keys: set
                        "card"          # Foreign keys: energy, rarity, rule, set, supertype
                    ],
                    [
                        "ability",      # Foreign keys: card
                        "attack",       # Foreign keys: card
                        "card_booster"  # Foreign keys: card, booster
                    ]
                ]

                for group in table_groups:
                    execute_sql_files(cur, conn, group, table_dir)

            # Connection auto-commits due to context manager
            print("✅ All tables created successfully.")

    except Exception as e:
        print(f"❗ Database setup failed: {e}")


if __name__ == "__main__":
    build_tables()
