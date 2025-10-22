import pytest
from unittest.mock import patch, MagicMock
from dao.userDao import UserDao


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
    next_id = [2]

    # Mocks connect/conn/cursor
    patcher = patch("dao.userDao.psycopg2.connect")
    mock_connect = patcher.start()

    mock_conn = MagicMock(name="conn")
    mock_cursor = MagicMock(name="cursor")

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Side_effect
    def execute_side_effect(sql, params=None):
        q = " ".join(sql.split()).strip().lower()

        # INSERT
        if q.startswith("insert into users"):
            # email unicity
            username, email, pwd = params
            for user in fake_users_db.values():
                if user["email"] == email:
                    from psycopg2 import IntegrityError

                    raise IntegrityError(
                        "duplicate key value violates unique "
                        "constraint 'users_email_key'"
                    )

            new_id = next_id[0]
            next_id[0] += 1
            fake_users_db[new_id] = {
                "id": new_id,
                "username": username,
                "email": email,
                "password_hash": pwd,
            }
            # RETURNING id, username, email, password_hash
            mock_cursor.fetchone.return_value = fake_users_db[new_id]
            mock_cursor.fetchall.return_value = [fake_users_db[new_id]]
            return

        # SELECT * FROM users WHERE id = %s LIMIT 1 (exist)
        if (
            q.startswith("select")
            and "from users" in q
            and "where id = %s" in q
            and "limit 1" in q
        ):
            id = params[0]
            row = fake_users_db.get(id)
            mock_cursor.fetchone.return_value = row
            mock_cursor.fetchall.return_value = [row] if row else []
            return

        # SELECT id, username, ... FROM users WHERE id = %s (get_by_id)
        if (
            q.startswith("select")
            and "from users" in q
            and "where id = %s" in q
        ):
            id = params[0]
            row = fake_users_db.get(id)
            mock_cursor.fetchone.return_value = row
            mock_cursor.fetchall.return_value = [row] if row else []
            return

        # SELECT ... FROM users ORDER BY id (get_all)
        if q.startswith("select") and "from users" in q and "order by id" in q:
            rows = [fake_users_db[k] for k in sorted(fake_users_db.keys())]
            mock_cursor.fetchall.return_value = rows
            mock_cursor.fetchone.return_value = rows[0] if rows else None
            return

        # UPDATE users SET ... WHERE id = %s RETURNING ...
        if q.startswith("update users"):
            id = params[-1]
            if id not in fake_users_db:
                mock_cursor.fetchone.return_value = None
                return
            updates_part = q.split("set")[1].split("where")[0]
            assignements = [a.strip() for a in updates_part.split(",")]
            values = params[:-1]
            record = fake_users_db[id].copy()
            i = 0
            for a in assignements:
                if a.startswith("username = %s"):
                    record["username"] = values[i]
                    i += 1
                elif a.startswith("email = %s"):
                    record["email"] = values[i]
                    i += 1
                elif a.startswith("password_hash = %s"):
                    record["password_hash"] = values[i]
                    i += 1
            fake_users_db[id] = record
            mock_cursor.fetchone.return_value = record
            mock_cursor.fetchall.return_value = [record]
            return

        # DELETE FROM users WHERE id = %s RETURNING ...
        if q.startswith("delete from users"):
            id = params[0]
            row = fake_users_db.pop(id, None)
            mock_cursor.fetchone.return_value = row
            mock_cursor.fetchall.return_value = [row] if row else []
            return

        # Default
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []

    mock_cursor.execute.side_effect = execute_side_effect

    yield UserDao(), mock_connect, mock_conn, mock_cursor, fake_users_db

    patcher.stop()


# Tests exist()
def test_exist_true(mock_user_dao):
    dao, _, _, _, _ = mock_user_dao
    assert dao.exist(1) is True


def test_exist_false(mock_user_dao):
    dao, _, _, _, _ = mock_user_dao
    assert dao.exist(50) is False


def test_exist_typeerror(mock_user_dao):
    dao, *_ = mock_user_dao
    with pytest.raises(TypeError):
        dao.exist("abc")


def test_exist_valueerror(mock_user_dao):
    dao, *_ = mock_user_dao
    with pytest.raises(ValueError):
        dao.exist(-1)


# Tests create()
def test_create_ok(mock_user_dao):
    dao, _, mock_conn, _, fake_db = mock_user_dao
    user = dao.create("hermione", "hermion@hogwarts.com", "hash2")
    assert (
        user["id"] in fake_db and fake_db[user["id"]]["username"] == "hermione"
    )
    mock_conn.commit.assert_called_once()


def test_create_duplicate_email(mock_user_dao):
    dao, *_ = mock_user_dao
    # already used email
    with pytest.raises(ValueError):
        dao.create("dup", "harry@hogwarts.com", "hashX")


# Tests get_all()
def test_get_all(mock_user_dao):
    dao, _, mock_conn, _, _ = mock_user_dao
    users = dao.get_all()
    assert isinstance(users, list)
    assert users and users[0]["id"] == 1
    mock_conn.commit.assert_not_called()


# Tests get_by_id()
def test_get_by_id_found(mock_user_dao):
    dao, _, mock_conn, _, _ = mock_user_dao
    u = dao.get_by_id(1)
    assert u and u["username"] == "harry"
    mock_conn.commit.assert_not_called()


def test_get_by_id_not_found(mock_user_dao):
    dao, *_ = mock_user_dao
    assert dao.get_by_id(999) is None


def test_get_by_id_typeerror(mock_user_dao):
    dao, *_ = mock_user_dao
    with pytest.raises(TypeError):
        dao.get_by_id("x")


# Tests update()
def test_update_username(mock_user_dao):
    dao, _, mock_conn, _, fake_db = mock_user_dao
    res = dao.update(1, username="potter")
    assert res["username"] == "potter"
    assert fake_db[1]["username"] == "potter"
    mock_conn.commit.assert_called_once()


def test_update_no_fields(mock_user_dao):
    dao, *_ = mock_user_dao
    with pytest.raises(ValueError):
        dao.update(1)


def test_update_valueerror_id(mock_user_dao):
    dao, *_ = mock_user_dao
    with pytest.raises(ValueError):
        dao.update(0, username="x")


# Tests delete()
def test_delete_found(mock_user_dao):
    dao, _, mock_conn, _, fake_db = mock_user_dao
    res = dao.delete(1)
    assert res and res["id"] == 1
    assert 1 not in fake_db
    mock_conn.commit.assert_called_once()


def test_delete_not_found(mock_user_dao):
    dao, *_ = mock_user_dao
    res = dao.delete(999)
    assert res is None
