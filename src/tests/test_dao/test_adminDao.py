import pytest
from unittest.mock import patch, MagicMock
from dao.adminDao import AdminDao


@pytest.fixture
def mock_user_dao():
    # Fake database to test userDao
    fake_users_db = {
        1: {
            "id": 1,
            "username": "harry",
            "email": "harry@hogwarts.com",
            "password_hash": "hash1",
        }
    }
    # Mocks connect/conn/cursor
    patcher = patch("dao.adminDao.psycopg2.connect")
    mock_connect = patcher.start()

    mock_conn = MagicMock(name="conn")
    mock_cursor = MagicMock(name="cursor")

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Side_effect
    def execute_side_effect(sql, params=None):
        q = " ".join(sql.split()).strip().lower()

        # SELECT ... FROM users ORDER BY id (get_all)
        if q.startswith("select") and "from users" in q and "order by id" in q:
            rows = [fake_users_db[k] for k in sorted(fake_users_db.keys())]
            mock_cursor.fetchall.return_value = rows
            mock_cursor.fetchone.return_value = rows[0] if rows else None
            return

    mock_cursor.execute.side_effect = execute_side_effect

    yield AdminDao(), mock_connect, mock_conn, mock_cursor, fake_users_db

    patcher.stop()


# Tests get_all()
def test_get_all(mock_user_dao):
    dao, _, mock_conn, _, _ = mock_user_dao
    users = dao.get_all()
    assert isinstance(users, list)
    assert users and users[0]["id"] == 1
    mock_conn.commit.assert_not_called()
