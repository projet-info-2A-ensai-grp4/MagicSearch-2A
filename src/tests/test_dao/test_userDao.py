import pytest
from unittest.mock import MagicMock, patch
from dao.userDao import UserDao


@pytest.fixture
def mock_user_dao():
    with patch("dao.userDao.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        fake_users_db = {
            56: {
                "user_id": 56,
                "username": "Harry Potter",
                "email": "harry@hogwarts.com",
                "password_hash": "x",
            }
        }
        next_id = [max(fake_users_db.keys()) + 1 if fake_users_db else 1]

        def execute_side_effect(sql, params=None):
            q = " ".join(sql.split()).strip().lower()

            if q.startswith("insert into users"):
                new_id = next_id[0]
                next_id[0] += 1

                username, email, pwd = params
                fake_users_db[new_id] = {
                    "user_id": new_id,
                    "username": username,
                    "email": email,
                    "password_hash": pwd,
                }

                mock_cursor.fetchone.return_value = (new_id,)
                return

            if q.startswith("select") and "from users" in q and "where" in q:
                uid = params[0] if params else None
                row = fake_users_db.get(uid)
                mock_cursor.fetchone.return_value = row
                return

            if q.startswith("select") and "from users" in q:
                mock_cursor.fetchall.return_value = list(fake_users_db.values())
                return

            mock_cursor.fetchone.return_value = None

        mock_cursor.execute.side_effect = execute_side_effect

        dao = UserDao()
        yield dao, mock_cursor, fake_users_db


def test_exist(mock_user_dao):
    """
    Tests if an ID is well detected into the database.
    Tests if a negative ID, or a non-integer ID is detected by the function.
    """
    dao, cursor, fake_users_db = mock_user_dao
    assert dao.exist(56) is True
    assert dao.exist(99) is False
    with pytest.raises(ValueError, match="ID must be a positive integer"):
        dao.exist(-1)
    with pytest.raises(TypeError, match="User ID must be an integer"):
        dao.exist("A")
    cursor.execute.assert_called()


def test_create(mock_user_dao):
    """
    Tests if a user is well created in the database.
    """
    dao, cursor, fake_users_db = mock_user_dao
    new_user_id = dao.create("Hermione Granger",
                             "hermione@hogwarts.com",
                             "5d41402abc4b2a76b9719d911017c592")
    assert isinstance(new_user_id, int)
    assert new_user_id == 57


def test_get_all(mock_user_dao):
    dao, cursor, fake_users_db = mock_user_dao
    dao.create("Hermione Granger",
               "hermione@hogwarts.com",
               "xx")
    rows = dao.get_all()
    assert isinstance(rows, list)
    assert rows == [
        {"user_id": 56,
         "username": "Harry Potter",
         "email": "harry@hogwarts.com",
         "password_hash": "x"},
        {"user_id": 57,
         "username": "Hermione Granger",
         "email": "hermione@hogwarts.com",
         "password_hash": "xx"}
    ]


def test_get_by_id(mock_user_dao):
    dao, cursor, fake_users_db = mock_user_dao
    user1 = dao.get_by_id(56)
    user2 = dao.get_by_id(99)
    assert user1 == {
         "user_id": 56,
         "username": "Harry Potter",
         "email": "harry@hogwarts.com",
         "password_hash": "x"}
    assert user2 is None
