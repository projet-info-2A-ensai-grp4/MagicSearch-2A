import pytest
from unittest.mock import MagicMock, patch
from dao.cardDao import CardDao

pytestmark = pytest.mark.filterwarnings(
    "ignore::UserWarning"
)  # Used to warn user that None was returned (in case the card is non existent)


@pytest.fixture
def mock_card_dao():
    """
    Provides a CardDao instance whose database calls are mocked.
    Simulates a database with cards stored in a dict keyed by ID.
    """
    # Base fake card
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
        "embedding": [0.1, 0.2, 0.3],  # correction : vrai list Python
        "raw": '{"rarity": "rare", "artist": "John Doe"}',
    }

    # Simulated DB: dict[id] -> card
    fake_db = {420: base_card.copy()}
    next_id = [421]

    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # make "with conn.cursor() as cur:" work
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_cursor.execute.return_value = None

        dao = CardDao()

        # fetchone side effect
        def fetchone_side_effect(*args, **kwargs):
            if not mock_cursor.execute.call_args:
                return None
            last_query = mock_cursor.execute.call_args[0][0]
            params = (
                mock_cursor.execute.call_args[0][1]
                if len(mock_cursor.execute.call_args[0]) > 1
                else None
            )
            sql = last_query.strip().upper()

            # --- COUNT ---
            if "COUNT(*)" in sql:
                return {"count": len(fake_db)}
            # --- INSERT ---
            if sql.startswith("INSERT"):
                card_data = {col: None for col in dao.columns_valid if col != "id"}
                if params:
                    for i, key in enumerate(card_data.keys()):
                        if i < len(params):
                            card_data[key] = params[i]
                card_data["id"] = next_id[0]
                next_id[0] += 1
                fake_db[card_data["id"]] = card_data
                return card_data

            # --- SELECT ---
            elif sql.startswith("SELECT"):
                card_id = params[0]
                return fake_db.get(card_id)

            # --- UPDATE ---
            elif sql.startswith("UPDATE"):
                card_id = params[-1]
                if card_id in fake_db:
                    set_part = sql.split("SET")[1].split("WHERE")[0]
                    cols = [
                        part.split("=")[0].strip().lower()
                        for part in set_part.split(",")
                    ]
                    for i, col in enumerate(cols):
                        if i < len(params) - 1:
                            fake_db[card_id][col] = params[i]
                    return fake_db[card_id]
                return None

            # --- DELETE ---
            elif sql.startswith("DELETE"):
                card_id = params[0]
                return fake_db.pop(card_id, None)

            return None

        mock_cursor.fetchone.side_effect = fetchone_side_effect

        yield dao, mock_cursor, fake_db


# -----------------------
# Tests
# -----------------------


def test_shape(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    row_count, col_count = dao.shape()
    assert row_count == len(fake_db)
    assert col_count == len(dao.columns_valid)
    cursor.execute.assert_called()


def test_exist(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    assert dao.exist(420) is True
    assert dao.exist(999) is False
    with pytest.raises(ValueError):
        dao.exist(-1)
    with pytest.raises(TypeError):
        dao.exist("A")
    cursor.execute.assert_called()


def test_get_by_id(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    card = dao.get_by_id(420)
    assert card is not None
    assert card["id"] == 420
    assert dao.get_by_id(999) is None
    with pytest.raises(TypeError):
        dao.get_by_id("")
    with pytest.raises(ValueError):
        dao.get_by_id(-1)
    cursor.execute.assert_called()


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

    fake_db[421] = fake_db[420].copy()
    fake_db[421]["id"] = 421
    fake_db[421]["name"] = "Other Card"
    fake_db[421]["type"] = "Artifact"

    expected_rows = [fake_db[420]]
    mock_cursor.fetchall.return_value = expected_rows
    results = dao.filter(order_by="id", type="Creature")
    query, params = mock_cursor.execute.call_args[0]
    assert "SELECT * FROM cards" in query
    assert "WHERE TRUE AND type = %s" in query
    assert "ORDER BY id ASC" in query
    assert "LIMIT %s OFFSET %s" in query
    assert params[:-2] == ["Creature"]
    assert params[-2:] == [100, 0]
    assert results == expected_rows


def test_get_card_by_id_nonexistent(card_dao):
    """Test fetching a card by a non-existent ID."""
    nonexistent_card_id = 99999
    result = card_dao.get_card_by_id(nonexistent_card_id)
    assert result is None, "Expected None for non-existent card ID"


def test_edit_text_to_embed(card_dao):
    """Test editing the text_to_embed value."""
    test_text = "This is a sample text to embed"
    test_card_id = 420

    # Edit the text_to_embed value
    result = card_dao.edit_text_to_embed(test_text, test_card_id)
    assert result == 1, "Expected 1 row to be updated"

    # Verify the update
    updated_card = card_dao.get_card_by_id(test_card_id)
    assert updated_card is not None, "Card not found after update"
    assert (
        updated_card["text_to_embed"] == test_text
    ), "text_to_embed was not updated correctly"


def test_edit_text_to_embed_nonexistent(card_dao):
    """Test editing the text_to_embed value for a non-existent card ID."""
    test_text = "This is a sample text to embed"
    nonexistent_card_id = 99999

    with pytest.raises(
        ValueError, match=f"No card found with ID {nonexistent_card_id}"
    ):
        card_dao.edit_text_to_embed(test_text, nonexistent_card_id)


def test_edit_vector_nonexistent(card_dao):
    """Test editing the embedding value for a non-existent card ID."""
    test_vector = [0.1, 0.2, 0.3]
    nonexistent_card_id = 99999

    with pytest.raises(
        ValueError, match=f"No card found with ID {nonexistent_card_id}"
    ):
        card_dao.edit_vector(test_vector, nonexistent_card_id)


def test_edit_vector(card_dao):
    """Test editing the embeddint value for a card ID."""
    test_vector = [0.1, 0.2, 0.3]
    test_card_id = 420

    result = card_dao.edit_vector(test_vector, test_card_id)
    assert result == 1

    # Verify the update
    updated_card = card_dao.get_card_by_id(test_card_id)
    assert updated_card is not None, "Card not found after update"
    assert (
        updated_card["embedding"] == test_vector
    ), "embedding value was not updated correctly"


def test_get_card_by_id_invalid_input(card_dao):
    """Test fetching a card by an invalid ID."""
    invalid_card_id = -1
    with pytest.raises(ValueError, match="card_id must be a positive integer"):
        card_dao.get_card_by_id(invalid_card_id)


def test_edit_text_to_embed_invalid_input(card_dao):
    """Test editing the text_to_embed value with an invalid card ID."""
    test_text = "This is a sample text to embed"
    invalid_card_id = -1
    with pytest.raises(ValueError, match="card_id must be a positive integer"):
        card_dao.edit_text_to_embed(test_text, invalid_card_id)


def test_edit_vector_invalid_input(card_dao):
    """Test editing the vector value with an invalid card ID."""
    test_vector = [0.1, 0.2, 0.3]
    invalid_card_id = -1
    with pytest.raises(ValueError, match="card_id must be a positive integer"):
        card_dao.edit_vector(test_vector, invalid_card_id)
