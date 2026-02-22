import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config.settings import Config

class Database:
    """
    Singleton class to manage PostgreSQL connection pool.
    """
    _pool = None

    @classmethod
    def initialize(cls):
        """Initialize the connection pool if it doesn't exist."""
        if cls._pool is None:
            try:
                # Use DATABASE_URL if provided, otherwise individual params
                if Config.DATABASE_URL:
                    cls._pool = psycopg2.pool.ThreadedConnectionPool(
                        minconn=1,
                        maxconn=20,
                        dsn=Config.DATABASE_URL
                    )
                else:
                    cls._pool = psycopg2.pool.ThreadedConnectionPool(
                        minconn=1,
                        maxconn=20,
                        database=Config.DB_NAME,
                        user=Config.DB_USER,
                        password=Config.DB_PASSWORD,
                        host=Config.DB_HOST,
                        port=Config.DB_PORT
                    )
                print("Database connection pool initialized.")
            except psycopg2.Error as e:
                print(f"Error connecting to database: {e}")
                raise e

    @classmethod
    def get_connection(cls):
        """Get a connection from the pool."""
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool."""
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    def close_pool(cls):
        """Close all connections in the pool."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            print("Database connection pool closed.")

@contextmanager
def get_db_connection():
    """
    Context manager for getting a database connection.
    Automatically returns the connection to the pool.
    """
    conn = Database.get_connection()
    try:
        yield conn
    finally:
        Database.return_connection(conn)

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for getting a database cursor.
    Handles commit/rollback automatically if commit=True.
    """
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        Database.return_connection(conn)
