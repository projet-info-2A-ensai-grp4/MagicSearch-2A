import sqlite3
import pytest


@pytest.fixture
def fake_user_table():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE users (
    userId INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    passwordHash TEXT)
    """)
    conn.commit()
    yield conn
    conn.close()
