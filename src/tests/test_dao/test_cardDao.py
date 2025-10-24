import pytest
from unittest.mock import MagicMock, patch
from dao.cardDao import CardDao

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")
# Used to warn user that None was returned#
#  (in case the card is non existent)#


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
        "embedding": "[0.1, 0.2, 0.3]",
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

        dao = CardDao()

        # fetchone side effect
        def fetchone_side_effect(*args, **kwargs):
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
                else:
                    return None

            # --- DELETE ---
            elif sql.startswith("DELETE"):
                card_id = params[0]
                return fake_db.pop(card_id, None)

            return None

        mock_cursor.fetchone.side_effect = fetchone_side_effect
        yield dao, mock_cursor, fake_db


def test_shape(mock_card_dao):
    """Test the shape method of the DAO."""
    dao, cursor, fake_db = mock_card_dao
    row_count, col_count = dao.shape()
    assert row_count == len(fake_db)
    assert col_count == len(dao.columns_valid)
    cursor.execute.assert_called()


def test_exist(mock_card_dao):
    """Tests if a card exists with its id"""
    dao, cursor, fake_db = mock_card_dao
    result_True = dao.exist(420)
    result_False = dao.exist(999)
    assert result_True is True
    assert result_False is False
    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.exist(-1)
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        dao.exist("A")
    cursor.execute.assert_called()


def test_get_by_id(mock_card_dao):
    """Test fetching a card by ID."""
    dao, cursor, fake_db = mock_card_dao
    card = dao.get_by_id(420)
    card_none = dao.get_by_id(999)
    assert card is not None
    assert card["id"] == 420
    # Non-existent Card
    assert card_none is None
    # Unvalide id
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        dao.get_by_id("")
    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.get_by_id(-1)
    cursor.execute.assert_called()


def test_create(mock_card_dao):
    """Test creating a card with a sample of valid and invalid inputs."""
    dao, cursor, fake_db = mock_card_dao
    # Valid creation
    created_card = dao.create(name="New Card", type="Spell", mana_value=1)
    assert created_card["id"] in fake_db
    assert created_card["name"] == "New Card"
    assert created_card["type"] == "Spell"
    assert created_card["mana_value"] == 1
    another_card = dao.create(name="Second Card")
    assert another_card["id"] != created_card["id"]
    assert another_card["name"] == "Second Card"
    # RETURNING * calling
    cursor.execute.assert_called()
    # invalide keys
    with pytest.raises(ValueError, match="Invalid keys"):
        dao.create(nonexistent_column="Oops")


def test_update(mock_card_dao):
    """Test updating a card, with Id and items who should be change"""
    dao, cursor, fake_db = mock_card_dao
    updated_card = dao.update(420, name="Updated Card")
    assert updated_card["id"] == 420
    assert updated_card["name"] == "Updated Card"
    # Non-existent card
    result_none = dao.update(999, {"name": "No Card"})
    assert result_none is None
    # Invalid Id
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        dao.update("abc", {"name": "Test"})
    # Non positive Id
    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.update(-1, name="Updated Card")
    cursor.execute.assert_called()


def test_delete(mock_card_dao):
    """Test deleting a card with various scenarios."""
    dao, cursor, fake_db = mock_card_dao
    result = dao.delete(420)
    assert result["name"] == "Example Card"
    assert dao.exist(420) is False
    # Non-existent card
    result_false = dao.delete(999)
    assert result_false is None
    # Invalid Id type
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        dao.delete("abc")
    # Non positive Id
    with pytest.raises(ValueError, match="Card ID must be a positive integer"):
        dao.delete(-1)
    cursor.execute.assert_called()
