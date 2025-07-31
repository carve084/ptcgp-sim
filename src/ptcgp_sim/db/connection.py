import psycopg2
from psycopg2 import pool, OperationalError
from threading import Lock
from contextlib import contextmanager

from src.ptcgp_sim.db.config import DatabaseConfig


class SingleConnectionManager:
    """
    Singleton for managing a single reusable database connection.
    Not intended for concurrent access.
    """
    _cursor = None
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        config = DatabaseConfig()
        try:
            self._conn = psycopg2.connect(
                host=config.host,
                dbname=config.dbname,
                user=config.user,
                password=config.password,
                port=config.port
            )
            self._cursor = self._conn.cursor()
        except OperationalError as e:
            raise RuntimeError(f"Failed to connect to the database: {e}")

    def get_connection(self):
        return self._conn

    def cursor(self):
        # Optionally poll to refresh connection
        # noinspection PyBroadException
        try:
            self._conn.poll()
        except Exception:
            self.reset_cursor()
        return self._cursor

    def reset_cursor(self):
        if hasattr(self, "_conn") and self._conn:
            self._cursor.close()
            self._cursor = self._conn.cursor()
        else:
            raise RuntimeError("Connection not initialized. Cannot reset cursor.")
        return self._cursor

    def close(self):
        if hasattr(self, "_conn") and self._conn:
            self._cursor.close()
            self._conn.close()
            type(self)._instance = None  # Reset singleton


class PooledConnectionManager:
    """
    Manages a thread-safe pool of database connections.
    """
    _pool = None
    _lock = Lock()

    @classmethod
    def initialize_pool(cls, minconn=1, maxconn=10):
        if cls._pool is None:
            with cls._lock:
                if cls._pool is None:
                    config = DatabaseConfig()
                    try:
                        cls._pool = psycopg2.pool.SimpleConnectionPool(
                            minconn=minconn,
                            maxconn=maxconn,
                            user=config.user,
                            password=config.password,
                            host=config.host,
                            port=config.port,
                            database=config.dbname
                        )
                    except OperationalError as e:
                        raise RuntimeError(f"Failed to create connection pool: {e}")

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            raise RuntimeError("Connection pool is not initialized.")
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        if cls._pool and conn:
            cls._pool.putconn(conn)

    @classmethod
    @contextmanager
    def connection(cls):
        """
        Use as:
            with PooledConnectionManager.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = cls.get_connection()
        try:
            yield conn
        finally:
            cls.return_connection(conn)

    @classmethod
    def close_all_connections(cls):
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None


class DatabaseConnection:
    """
    Factory for retrieving database connection managers.
    """

    @staticmethod
    def get(pooled=False, minconn=1, maxconn=10):
        if pooled:
            PooledConnectionManager.initialize_pool(minconn, maxconn)
            return PooledConnectionManager
        else:
            return SingleConnectionManager()
