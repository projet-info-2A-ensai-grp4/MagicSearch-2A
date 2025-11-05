import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()


@contextmanager
def dbConnection():
    """Context manager for database connections."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    try:
        yield conn
    finally:
        conn.close()
