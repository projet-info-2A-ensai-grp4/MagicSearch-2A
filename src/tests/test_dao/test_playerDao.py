import pytest
from unittest.mock import MagicMock, patch
import psycopg2
from dao.playerDao import PlayerDao


@pytest.fixture
def mock_player_db():
    with (
        patch("dao.playerDao.dbConnection") as mock_db_conn,
        patch("dao.playerDao.register_vector") as mock_register_vector,
    ):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # dbConnection() as conn: -> conn
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        # conn.cursor(...) as cursor: -> cursor
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Basic cursor behavior
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "name": "Card One",
                "text": "Some text",
                "type": "Creature",
                "color_identity": "G",
                "mana_cost": "{1}{G}",
                "scryfall_oracle_id": "id-1",
                "distance": 0.12,
            }
        ]
        mock_cursor.fetchone.return_value = {"embedding": [0.1, 0.2, 0.3]}

        yield mock_conn, mock_cursor


def test_natural_language_search_with_text_query(mock_player_db):
    mock_conn, mock_cursor = mock_player_db
    embedding_service = MagicMock()
    embedding_service.vectorize.return_value = [0.1, 0.2, 0.3]

    dao = PlayerDao(embedding_service=embedding_service)
    results = dao.natural_language_search("find me similar", limit=2)

    assert results == mock_cursor.fetchall.return_value
    embedding_service.vectorize.assert_called_once_with("find me similar")
    mock_cursor.execute.assert_called_once()
    sql, params = mock_cursor.execute.call_args[0]
    assert params[0] == [0.1, 0.2, 0.3]
    assert params[-1] == 2


def test_natural_language_search_with_vector_query_uses_vector_directly(mock_player_db):
    mock_conn, mock_cursor = mock_player_db
    embedding_service = MagicMock()

    dao = PlayerDao(embedding_service=embedding_service)
    vec = [0.4, 0.5, 0.6]
    results = dao.natural_language_search(vec, limit=1)

    assert results == mock_cursor.fetchall.return_value
    embedding_service.vectorize.assert_not_called()
    mock_cursor.execute.assert_called_once()
    _, params = mock_cursor.execute.call_args[0]
    assert params[0] == vec
    assert params[-1] == 1


def test_natural_language_search_with_filters_includes_conditions(mock_player_db):
    mock_conn, mock_cursor = mock_player_db
    embedding_service = MagicMock()
    embedding_service.vectorize.return_value = [0.0]

    dao = PlayerDao(embedding_service=embedding_service)
    filters = {"color_identity": "G", "type": "Creature"}
    dao.natural_language_search("q", filters=filters, limit=5)

    mock_cursor.execute.assert_called_once()
    sql, params = mock_cursor.execute.call_args[0]
    sql_upper = sql.upper()
    assert "WHERE" in sql_upper
    # Ensure both filter columns appear in SQL
    assert "COLOR_IDENTITY = %S" in sql_upper or "COLOR_IDENTITY =" in sql_upper
    assert "TYPE = %S" in sql_upper or "TYPE =" in sql_upper
    # Params should include filter values and then limit
    assert "G" in params
    assert "Creature" in params
    assert params[-1] == 5


def test_natural_language_search_invalid_limit_raises():
    dao = PlayerDao(embedding_service=MagicMock())
    with pytest.raises(ValueError):
        dao.natural_language_search("q", limit=0)


def test_natural_language_search_invalid_query_type_raises():
    dao = PlayerDao(embedding_service=MagicMock())
    with pytest.raises(ValueError):
        dao.natural_language_search(12345, limit=1)


def test_get_card_embedding_returns_vector(mock_player_db):
    mock_conn, mock_cursor = mock_player_db
    dao = PlayerDao(embedding_service=MagicMock())
    embedding = dao.get_card_embedding(42)
    assert embedding == mock_cursor.fetchone.return_value["embedding"]
    mock_cursor.execute.assert_called_once_with(
        "SELECT embedding FROM cards WHERE id = %s", (42,)
    )


def test_get_card_embedding_none_returns_none():
    with (
        patch("dao.playerDao.dbConnection") as mock_db_conn,
        patch("dao.playerDao.register_vector"),
    ):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        dao = PlayerDao(embedding_service=MagicMock())
        assert dao.get_card_embedding(999) is None


def test_natural_language_search_raises_connection_error_on_db_failure():
    with patch(
        "dao.playerDao.dbConnection", side_effect=psycopg2.OperationalError("conn fail")
    ):
        dao = PlayerDao(embedding_service=MagicMock())
        with pytest.raises(ConnectionError):
            dao.natural_language_search("x", limit=1)


def test_natural_language_search_raises_runtime_error_on_unexpected_db_error(
    mock_player_db,
):
    mock_conn, mock_cursor = mock_player_db
    mock_cursor.execute.side_effect = Exception("boom")
    dao = PlayerDao(embedding_service=MagicMock())
    with pytest.raises(RuntimeError):
        dao.natural_language_search([0.1], limit=1)
