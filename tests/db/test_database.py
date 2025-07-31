import psycopg2
import unittest

from ptcgp_sim.db import DatabaseConnection

# TODO: Unused for now

class TestDatabaseConnection(unittest.TestCase):
    def test_database_connection(self):
        # Create an instance of DatabaseConnection
        db = DatabaseConnection().get()
        self.assertTrue(db is not None, "Failed to establish a database connection.")

        # Get the cursor from the connection
        cursor = db.cursor()
        self.assertIsNotNone(cursor)

        # Execute a simple query to check if the connection works
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        self.assertEqual(result, (1,))

        # Close the connection
        db.close()

    def test_close_connection(self):
        # Create an instance of DatabaseConnection
        db = DatabaseConnection().get()
        self.assertTrue(db is not None, "Failed to establish a database connection.")

        # Close the connection
        db.close()

        # Attempt to execute a query after closing the connection
        with self.assertRaises(psycopg2.InterfaceError):
            db.cursor().execute("SELECT 1;")

    def test_singleton_connection(self):
        # Create a single instance of DatabaseConnection
        db1 = DatabaseConnection().get()
        cursor1 = db1.cursor()

        # Create another instance, which should return the same connection
        db2 = DatabaseConnection().get()
        cursor2 = db2.cursor()

        # Assert that both cursors are the same
        self.assertIs(cursor1, cursor2)

        # Execute a simple query using the first cursor
        cursor1.execute("SELECT 1;")

        # Assert that the second cursor can also fetch the result
        self.assertEqual(cursor2.fetchone(), (1,))

        # Close the connection
        db1.close()

    def test_reset_cursor(self):
        # Create an instance of DatabaseConnection
        db = DatabaseConnection().get()

        # Get the initial cursor
        initial_cursor = db.cursor()

        # Execute a simple query to check if the cursor works
        initial_cursor.execute("SELECT 1;")
        self.assertEqual(initial_cursor.fetchone(), (1,))

        # Reset the cursor
        new_cursor = db.reset_cursor()
        self.assertIsNot(initial_cursor, new_cursor, "Reset cursor should return a new cursor instance.")

        # Execute a simple query to check if the reset cursor works
        new_cursor.execute("SELECT 2;")
        self.assertEqual(new_cursor.fetchone(), (2,))

        # Attempt to execute a query with the old cursor after closing it
        with self.assertRaises(psycopg2.InterfaceError):
            initial_cursor.execute("SELECT 3;")

        # Close the connection
        db.close()

    def test_pooled_connection(self):
        # Initialize the pooled database connection
        db = DatabaseConnection().get(pooled=True, minconn=1, maxconn=5)

        # Get a connection from the pool
        conn = db.get_connection()
        self.assertIsNotNone(conn, "Failed to get a connection from the pool.")

        # Use the connection to create a cursor and execute a query
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        self.assertEqual(result, (1,))

        # Return the connection to the pool
        cursor.close()
        db.return_connection(conn)

        # Close all connections in the pool
        db.close_all_connections()
