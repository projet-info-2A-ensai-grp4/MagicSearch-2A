import pytest
from unittest.mock import MagicMock, patch
from dao.cardDao import CardDao
import copy

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


@pytest.fixture
def mock_card_dao():
    """Provides a CardDao instance with mocked database interactions."""
    with patch("dao.cardDao.psycopg2.connect") as mock_connect:
        base_card = {
            "id": 420,
            "card_key": "example_key",
            "name": "Example Card",
            "ascii_name": "Example Card",
            "text": "This is an example text for the card.",
            "type": "Creature",
            "layout": "normal",
            "mana_cost": "{1}{G}",
            "mana_value": 2,
            "converted_mana_cost": 2,
            "face_converted_mana_cost": 0,
            "face_mana_value": 0,
            "face_name": None,
            "first_printing": "2020-01-01",
            "hand": None,
            "life": None,
            "loyalty": None,
            "power": "2",
            "toughness": "2",
            "side": None,
            "defense": None,
            "edhrec_rank": 1234,
            "edhrec_saltiness": 0.5,
            "is_funny": 0,
            "is_game_changer": 0,
            "is_reserved": 0,
            "has_alternative_deck_limit": 0,
            "colors": "G",
            "color_identity": "G",
            "color_indicator": None,
            "types": "Creature",
            "subtypes": "Elf Druid",
            "supertypes": None,
            "keywords": "Trample",
            "subsets": None,
            "printings": "SET1",
            "scryfall_oracle_id": "550e8400-e29b-41d4-a716-446655440000",
            "text_to_embed": "Some text to embed",
            "embedding": [0.1, 0.2, 0.3],
            "raw": '{"rarity": "rare", "artist": "John Doe"}',
        }

        fake_db = {420: copy.deepcopy(base_card)}
        next_id = [421]

        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Context manager support
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_cursor.execute.return_value = None

        # fetchall returns deep copies to avoid mutation issues
        mock_cursor.fetchall.side_effect = lambda: [
            copy.deepcopy(v) for v in fake_db.values()
        ]

        # Create DAO instance - this will now use the mocked psycopg2.connect
        dao = CardDao()

        # fetchone side effect
        def fetchone_side_effect(*args, **kwargs):
            if not mock_cursor.execute.call_args:
                return None
            sql = mock_cursor.execute.call_args[0][0]
            sql_upper = (
                sql.strip().upper() if isinstance(sql, str) else str(sql).upper()
            )
            params = (
                mock_cursor.execute.call_args[0][1]
                if len(mock_cursor.execute.call_args[0]) > 1
                else None
            )

            if "COUNT(*)" in sql_upper:
                return {"count": len(fake_db)}

            if sql_upper.startswith("SELECT") and "WHERE ID = %S" in sql_upper:
                card_id = params[0]
                return copy.deepcopy(fake_db.get(card_id))

            # Handle ILIKE queries for search_by_name
            if "ILIKE" in sql_upper:
                return None  # Will use fetchall instead

            # Handle RANDOM() queries for get_random_card
            if "RANDOM()" in sql_upper:
                if fake_db:
                    return copy.deepcopy(list(fake_db.values())[0])
                return None

            if sql_upper.startswith("INSERT"):
                card_data = {k: None for k in dao.columns_valid if k != "id"}
                if params:
                    for i, key in enumerate(card_data.keys()):
                        if i < len(params):
                            card_data[key] = params[i]
                card_data["id"] = next_id[0]
                next_id[0] += 1
                fake_db[card_data["id"]] = copy.deepcopy(card_data)
                return copy.deepcopy(card_data)

            if "UPDATE" in sql_upper:
                if not params:
                    return None
                card_id = params[-1]
                if card_id in fake_db:
                    # Handle text_to_embed updates
                    if "TEXT_TO_EMBED" in sql_upper:
                        fake_db[card_id]["text_to_embed"] = params[0]
                        return copy.deepcopy(fake_db[card_id])
                    # Handle embedding updates
                    if "EMBEDDING" in sql_upper:
                        fake_db[card_id]["embedding"] = params[0]
                        return copy.deepcopy(fake_db[card_id])
                    # Handle general updates
                    set_part = sql_upper.split("SET")[1].split("WHERE")[0]
                    cols = [
                        p.split("=")[0].strip().lower() for p in set_part.split(",")
                    ]
                    values = params[:-1]
                    for col, val in zip(cols, values):
                        fake_db[card_id][col] = val
                    return copy.deepcopy(fake_db[card_id])
                return None

            if sql_upper.startswith("DELETE"):
                card_id = params[0]
                return copy.deepcopy(fake_db.pop(card_id, None))

            return None

        mock_cursor.fetchone.side_effect = fetchone_side_effect

        yield dao, mock_cursor, fake_db


def test_shape(mock_card_dao):
    dao, mock_cursor, _ = mock_card_dao
    result = dao.shape()
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(x, int) for x in result)
    mock_cursor.execute.assert_called()
    assert "COUNT(*)" in mock_cursor.execute.call_args[0][0].upper()


def test_exist(mock_card_dao):
    dao, cursor, _ = mock_card_dao
    assert isinstance(dao.exist(420), bool)
    assert isinstance(dao.exist(999), bool)
    with pytest.raises(ValueError):
        dao.exist(-1)
    with pytest.raises(TypeError):
        dao.exist("A")
    cursor.execute.assert_called()


def test_get_by_id(mock_card_dao):
    dao, cursor, _ = mock_card_dao
    card = dao.get_by_id(420)
    assert card is None or isinstance(card, dict)
    with pytest.raises(TypeError):
        dao.get_by_id("")
    with pytest.raises(ValueError):
        dao.get_by_id(-1)
    cursor.execute.assert_called()
    last_query = cursor.execute.call_args[0][0].upper()
    assert "SELECT" in last_query
    assert "WHERE ID" in last_query


def test_create(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    created_card = dao.create(name="New Card", type="Spell", mana_value=1)
    assert created_card["id"] in fake_db
    assert created_card["name"] == "New Card"
    assert created_card["type"] == "Spell"
    assert created_card["mana_value"] == 1
    with pytest.raises(ValueError):
        dao.create(nonexistent_column="Oops")


def test_update(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    updated_card = dao.update(420, name="Updated Card")
    assert updated_card["name"] == "Updated Card"
    assert dao.update(999, {"name": "No Card"}) is None
    with pytest.raises(TypeError):
        dao.update("abc", {"name": "Test"})
    with pytest.raises(ValueError):
        dao.update(-1, name="Updated Card")
    cursor.execute.assert_called()


def test_delete(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    result = dao.delete(420)
    assert result["name"] == "Example Card"
    assert dao.exist(420) is False
    assert dao.delete(999) is None
    with pytest.raises(TypeError):
        dao.delete("abc")
    with pytest.raises(ValueError):
        dao.delete(-1)
    cursor.execute.assert_called()


def test_filter_with_valid_kwargs(mock_card_dao):
    dao, mock_cursor, fake_db = mock_card_dao
    fake_db[421] = copy.deepcopy(fake_db[420])
    fake_db[421]["id"] = 421
    fake_db[421]["name"] = "Other Card"
    fake_db[421]["type"] = "Artifact"
    mock_cursor.fetchall.side_effect = lambda: [
        card for card in fake_db.values() if card["type"] == "Creature"
    ]
    results = dao.filter(order_by="id", type="Creature")
    query, params = mock_cursor.execute.call_args[0]
    assert "SELECT * FROM cards" in query
    assert "WHERE type = %s" in query
    assert "ORDER BY id ASC" in query
    assert "LIMIT %s OFFSET %s" in query
    assert params[0] == "Creature"
    assert params[-2:] == [10, 0]
    assert all(r["type"] == "Creature" for r in results)
    assert [r["id"] for r in results] == [420]


def test_edit_text_to_embed_valid(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    # Mock rowcount for successful update
    cursor.rowcount = 1

    result = dao.edit_text_to_embed("New embedded text", 420)

    assert result == 1
    cursor.execute.assert_called()
    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    # Convert SQL object to string for comparison
    query_str = str(query) if hasattr(query, "as_string") else query
    assert "UPDATE cards SET text_to_embed" in query_str or "text_to_embed" in query_str
    assert params == ("New embedded text", 420)
    dao.conn.commit.assert_called()


def test_edit_text_to_embed_invalid_type(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(TypeError, match="embed_me must be a string"):
        dao.edit_text_to_embed(123, 420)

    with pytest.raises(TypeError, match="embed_me must be a string"):
        dao.edit_text_to_embed(None, 420)


def test_edit_text_to_embed_empty_string(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="embed_me cannot be empty or whitespace only"):
        dao.edit_text_to_embed("", 420)

    with pytest.raises(ValueError, match="embed_me cannot be empty or whitespace only"):
        dao.edit_text_to_embed("   ", 420)


def test_edit_text_to_embed_invalid_card_id(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.edit_text_to_embed("Valid text", -1)

    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.edit_text_to_embed("Valid text", 0)

    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.edit_text_to_embed("Valid text", "abc")


def test_edit_text_to_embed_nonexistent_card(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    # Mock rowcount = 0 to simulate no rows updated
    cursor.rowcount = 0

    with pytest.raises(ValueError, match="No card found with ID 999"):
        dao.edit_text_to_embed("Valid text", 999)


def test_edit_vector_valid(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    # Mock rowcount for successful update
    cursor.rowcount = 1

    vector = [0.5, 0.6, 0.7, 0.8]
    result = dao.edit_vector(vector, 420)

    assert result == 1
    cursor.execute.assert_called()
    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    # Convert SQL object to string for comparison
    query_str = str(query) if hasattr(query, "as_string") else query
    assert "UPDATE cards SET embedding" in query_str or "embedding" in query_str
    assert params == (vector, 420)
    dao.conn.commit.assert_called()


def test_edit_vector_invalid_type(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(TypeError, match="vector_me must be a list"):
        dao.edit_vector("not a list", 420)

    with pytest.raises(TypeError, match="vector_me must be a list"):
        dao.edit_vector((0.1, 0.2), 420)


def test_edit_vector_empty_list(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="vector_me cannot be empty"):
        dao.edit_vector([], 420)


def test_edit_vector_non_numeric_values(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(TypeError, match="vector_me must contain only numeric values"):
        dao.edit_vector([0.1, "string", 0.3], 420)

    with pytest.raises(TypeError, match="vector_me must contain only numeric values"):
        dao.edit_vector([0.1, None, 0.3], 420)


def test_edit_vector_invalid_card_id(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    vector = [0.1, 0.2, 0.3]

    with pytest.raises(ValueError, match="card_id must be a positive integer"):
        dao.edit_vector(vector, -1)

    with pytest.raises(ValueError, match="card_id must be a positive integer"):
        dao.edit_vector(vector, 0)


def test_edit_vector_nonexistent_card(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    # Mock rowcount = 0 to simulate no rows updated
    cursor.rowcount = 0
    vector = [0.1, 0.2, 0.3]

    with pytest.raises(ValueError, match="No card found with ID 999"):
        dao.edit_vector(vector, 999)


def test_search_by_name_valid(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    # Mock search results - the mock will return fake_db values
    mock_results = [
        {"id": 420, "name": "Example Card", "type": "Creature"},
        {"id": 421, "name": "Example Spell", "type": "Instant"},
    ]

    # Clear the side_effect so return_value takes precedence
    cursor.fetchall.side_effect = None
    cursor.fetchall.return_value = mock_results

    results = dao.search_by_name("Example")

    assert len(results) == 2
    cursor.execute.assert_called()
    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]

    assert "SELECT" in query.upper()
    assert "WHERE name ILIKE %s OR ascii_name ILIKE %s" in query
    assert "ORDER BY name" in query
    assert "LIMIT %s OFFSET %s" in query
    assert params == ("%Example%", "%Example%", 20, 0)


def test_search_by_name_with_pagination(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    # Clear side_effect
    cursor.fetchall.side_effect = None
    cursor.fetchall.return_value = []

    dao.search_by_name("Card", limit=10, offset=5)

    params = cursor.execute.call_args[0][1]
    assert params[-2:] == (10, 5)


def test_search_by_name_empty_string(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="Search name cannot be empty"):
        dao.search_by_name("")

    with pytest.raises(ValueError, match="Search name cannot be empty"):
        dao.search_by_name("   ")


def test_search_by_name_invalid_limit(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="Limit must be positive"):
        dao.search_by_name("Card", limit=0)

    with pytest.raises(ValueError, match="Limit must be positive"):
        dao.search_by_name("Card", limit=-5)


def test_search_by_name_invalid_offset(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="Offset must be non-negative"):
        dao.search_by_name("Card", offset=-1)


def test_get_random_card_success(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    # Mock random card result
    mock_card = {
        "id": 420,
        "name": "Example Card",
        "type": "Creature",
        "mana_value": 2,
        "colors": ["G"],
        "image_url": "http://example.com/card.jpg",
    }
    cursor.fetchone.return_value = mock_card

    result = dao.get_random_card()

    assert result is not None
    assert result["id"] == 420
    assert result["name"] == "Example Card"
    cursor.execute.assert_called()
    query = cursor.execute.call_args[0][0]
    assert "SELECT" in query.upper()
    assert "ORDER BY RANDOM()" in query
    assert "LIMIT 1" in query


def test_get_random_card_empty_database(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    # Clear the fake database
    fake_db.clear()

    # Override fetchone to return None for empty database
    cursor.fetchone.side_effect = lambda: None

    result = dao.get_random_card()

    assert result is None


def test_filter_with_array_columns(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    cursor.fetchall.return_value = []

    # Test with array column (colors)
    dao.filter(order_by="id", colors=["R", "G"])

    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]

    assert "colors && %s" in query
    assert ["R", "G"] in params


def test_filter_with_comparison_operators(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    cursor.fetchall.return_value = []

    # Test with lte operator
    dao.filter(order_by="id", mana_value__lte=3)

    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]

    assert "mana_value <= %s" in query
    assert 3 in params


def test_filter_with_gte_operator(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    cursor.fetchall.return_value = []

    # Test with gte operator
    dao.filter(order_by="id", mana_value__gte=5)

    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]

    assert "mana_value >= %s" in query
    assert 5 in params


def test_filter_descending_order(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    cursor.fetchall.return_value = []

    dao.filter(order_by="id", asc=False)

    query = cursor.execute.call_args[0][0]
    assert "ORDER BY id DESC" in query


def test_filter_invalid_order_by_column(mock_card_dao):
    dao, cursor, _ = mock_card_dao

    with pytest.raises(ValueError, match="Invalid order_by"):
        dao.filter(order_by="invalid_column")


def test_filter_with_none_value(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao

    cursor.fetchall.return_value = []

    dao.filter(order_by="id", name=None)

    query = cursor.execute.call_args[0][0]
    assert "FALSE" in query


def test_edit_text_to_embed_with_context_manager(mock_card_dao):
    """Test that edit_text_to_embed works within context manager"""
    dao, cursor, fake_db = mock_card_dao

    # The method should use context manager internally
    cursor.rowcount = 1

    with patch.object(dao, "__enter__", return_value=dao):
        with patch.object(dao, "__exit__", return_value=None):
            dao.cursor = cursor
            dao.conn = MagicMock()
            result = dao.edit_text_to_embed("Context test", 420)

            assert result == 1
            dao.conn.commit.assert_called()


def test_edit_vector_with_mixed_numeric_types(mock_card_dao):
    """Test edit_vector accepts both int and float"""
    dao, cursor, fake_db = mock_card_dao

    cursor.rowcount = 1
    dao.cursor = cursor
    dao.conn = MagicMock()

    vector = [1, 2.5, 3, 4.7, 5]
    result = dao.edit_vector(vector, 420)

    assert result == 1


def test_search_by_name_case_insensitive(mock_card_dao):
    """Test search is case-insensitive"""
    dao, cursor, _ = mock_card_dao

    mock_results = [{"id": 420, "name": "Example Card"}]
    cursor.fetchall.return_value = mock_results

    # Search with different cases
    results1 = dao.search_by_name("EXAMPLE")
    results2 = dao.search_by_name("example")
    results3 = dao.search_by_name("ExAmPlE")

    # All should produce same query pattern
    for call in cursor.execute.call_args_list[-3:]:
        assert "ILIKE" in call[0][0]


def test_search_by_name_special_characters(mock_card_dao):
    """Test search handles special characters safely"""
    dao, cursor, _ = mock_card_dao

    cursor.fetchall.return_value = []

    # Should not raise exception with special chars
    dao.search_by_name("Card's Name")
    dao.search_by_name("Card-Name")
    dao.search_by_name("Card (Name)")

    assert cursor.execute.call_count >= 3


def test_search_by_name_returns_specific_columns(mock_card_dao):
    """Test that search_by_name only returns specific columns"""
    dao, cursor, _ = mock_card_dao

    cursor.fetchall.return_value = []
    dao.search_by_name("Test")

    query = cursor.execute.call_args[0][0]
    # Should not be SELECT *
    assert "SELECT id, name, ascii_name, type, mana_cost" in query
    assert "SELECT *" not in query


def test_get_random_card_returns_specific_columns(mock_card_dao):
    """Test that get_random_card returns specific columns"""
    dao, cursor, _ = mock_card_dao

    cursor.fetchone.return_value = {"id": 420, "name": "Test"}
    dao.get_random_card()

    query = cursor.execute.call_args[0][0]
    # Should select specific columns
    assert "SELECT id, name" in query
    assert "ORDER BY RANDOM()" in query


def test_filter_with_multiple_conditions(mock_card_dao):
    """Test filter with multiple WHERE conditions"""
    dao, cursor, _ = mock_card_dao

    cursor.fetchall.return_value = []

    dao.filter(order_by="id", type="Creature", mana_value__lte=3, colors=["G"])

    query = cursor.execute.call_args[0][0]
    assert "WHERE" in query
    assert "AND" in query
    assert query.count("AND") >= 2


def test_filter_with_list_on_non_array_column(mock_card_dao):
    """Test filter handles lists on non-array columns with IN clause"""
    dao, cursor, _ = mock_card_dao

    cursor.fetchall.return_value = []

    dao.filter(order_by="id", type=["Creature", "Artifact"])

    query = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]

    assert "type IN" in query
    assert "Creature" in params
    assert "Artifact" in params


def test_filter_validates_column_names_with_operators(mock_card_dao):
    """Test filter validates column names even with __lte/__gte operators"""
    dao, cursor, _ = mock_card_dao

    # Valid column with operator should work
    cursor.fetchall.return_value = []
    dao.filter(order_by="id", mana_value__lte=5)

    # Invalid column with operator should fail
    with pytest.raises(ValueError, match="Invalid keys"):
        dao.filter(order_by="id", invalid_col__lte=5)


def test_edit_text_to_embed_updates_correct_card(mock_card_dao):
    """Test that edit_text_to_embed updates the correct card"""
    dao, cursor, fake_db = mock_card_dao

    # Add another card
    fake_db[421] = copy.deepcopy(fake_db[420])
    fake_db[421]["id"] = 421
    fake_db[421]["text_to_embed"] = "Other text"

    cursor.rowcount = 1
    dao.cursor = cursor
    dao.conn = MagicMock()

    dao.edit_text_to_embed("Updated text", 420)

    # Verify the query targets the correct ID
    params = cursor.execute.call_args[0][1]
    assert params[1] == 420  # card_id parameter


def test_edit_vector_updates_correct_card(mock_card_dao):
    """Test that edit_vector updates the correct card"""
    dao, cursor, fake_db = mock_card_dao

    cursor.rowcount = 1
    dao.cursor = cursor
    dao.conn = MagicMock()

    vector = [0.9, 0.8, 0.7]
    dao.edit_vector(vector, 420)

    # Verify correct parameters
    params = cursor.execute.call_args[0][1]
    assert params[0] == vector
    assert params[1] == 420
