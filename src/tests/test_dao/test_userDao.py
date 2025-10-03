import pytest
from unittest.mock import MagicMock, patch
from psycopg2 import sql
from dao.userDao import UserDao


@pytest.fixture
def mock_user_dao():
    """
    Provides a UserDao instance whose database calls are mocked.
    Simulates a single card record with id=420.
    """
    fake_user = {
        "id": 56,
        "username": "Harry Potter",
        "email": "harrypotter@hogwarts.com",
        "password_hash": "5d41402abc4b2a76b9719d911017c592"}
    
    # Patch psycopg2.connect to return a mock connection
    with patch("dao.abstractDao.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate SELECT for exist/get_by_id
        def fetchone_side_effect():
            # Determine what query was executed
            last_sql, last_params = mock_cursor.execute.call_args[0]
            user_id = last_params[0]
            if "SELECT" in last_sql:
                if user_id == 56:
                    return (56, "Harry Potter")  # Simulate row exists
                return None  # Non-existent card
            return None

        mock_cursor.fetchone.side_effect = fetchone_side_effect

        # Inject DAO with mocked DB
        dao = UserDao()
        # Yield a tuple of dao and the mock cursor to let tests inspect calls
        yield dao, mock_cursor


def test_exist(mock_user_dao):
    """
    Tests if an ID is well detected into the database.
    Tests if a negative ID, or a non-integer ID is detected by the function.
    """
    dao, cursor = mock_user_dao
    result_True = dao.exist(56)
    result_False = dao.exist(99)
    assert result_True is True
    assert result_False is False
    with pytest.raises(ValueError, match="ID must be a positive integer"):
        dao.exist(-1)
    with pytest.raises(TypeError, match="User ID must be an integer"):
        dao.exist("A")
    cursor.execute.assert_called()


def test_create(mock_user_dao):
    """
    Tests if a user is well created in the database.
    """
    dao, cursor = mock_user_dao
    new_user_id = dao.create("Hermione Granger",
                             "hermione@hogwarts.com",
                             "5d41402abc4b2a76b9719d911017c592")
    assert new_user_id == 2
    cursor.execute.assert_called()


def test_get_by_id():
    pass

