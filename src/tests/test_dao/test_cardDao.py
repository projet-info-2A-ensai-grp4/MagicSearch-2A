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
    Simulates a single card record with id=420, returned as a dict
    (like RealDictCursor would do).
    """
    fake_card = {
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

    # Patch psycopg2.connect to return a mock connection
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate SELECT for exist/get_by_id
        def fetchone_side_effect():
            # Retrieve the last query params
            _, last_params = mock_cursor.execute.call_args[0]
            card_id = last_params[0]

            if card_id == 420:
                return fake_card  # RealDictCursor-like dict
            return None  # Simulate non-existent card

        mock_cursor.fetchone.side_effect = fetchone_side_effect

        # Inject DAO with mocked DB
        dao = CardDao()
        yield dao, mock_cursor


def test_exist(mock_card_dao):
    """Tests if a card exists with its id """
    dao, cursor = mock_card_dao
    result_True = dao.exist(420)
    result_False = dao.exist(999)
    assert result_True is True
    assert result_False is False
    with pytest.raises(ValueError, match="Id must be a positive integer"):
        dao.exist(-1)
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        dao.exist("A")
    cursor.execute.assert_called()


def test_get_by_id(mock_card_dao):
    """Test fetching a card by ID."""
    dao, cursor = mock_card_dao
    card = dao.get_by_id(420)
    card_none = dao.get_by_id(999)
    assert card is not None
    assert card["id"] == 420
    # Non-existent Card
    assert card_none is None
    # Unvalide id
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        dao.get_by_id("")
    with pytest.raises(ValueError, match="Id must be a positive integer"):
        dao.get_by_id(-1)
    cursor.execute.assert_called()


def test_create(mock_card_dao):
    """ Test creating a card with a samble of items """
    dao, cursor = mock_card_dao
    new_card = {"id": 421, "name": "New Card"}
    created_card = dao.create(new_card)
    assert created_card["id"] == 421
    assert created_card["name"] == "New Card"
    # Unvalid type of new_card
    with pytest.raises(TypeError, match="Card data must be a dictionary"):
        dao.create("not a dict")
    # unvalid id type
    with pytest.raises(TypeError, match="Card Id must be a positive integer"):
        dao.create({"id": "a", "name": "Duplicate Card"})
    # Duplicate case
    with pytest.raises(Exception, match="Card with this Id already exists"):
        dao.create({"id": 420, "name": "Duplicate Card"})
    # id non-negative
    with pytest.raises(TypeError, match="Card Id must be a positive integer"):
        dao.create({"id": -1, "name": "Duplicate Card"})
    cursor.execute.assert_called()


def test_update(mock_card_dao):
    """ Test updating a card, with Id and items who should be change """
    dao, cursor = mock_card_dao
    updated_data = {"name": "Updated Card"}
    updated_card = dao.update(420, updated_data)
    assert updated_card["id"] == 420
    assert updated_card["name"] == "Updated Card"
    # Non-existent card
    result_none = dao.update(999, {"name": "No Card"})
    assert result_none is None
    # Invalid Id
    with pytest.raises(TypeError, match="Card Id must be an integer"):
        dao.update("abc", {"name": "Test"})
    # Invalid update data
    with pytest.raises(TypeError, match="Update data must be a dictionary"):
        dao.update(420, "not a dict")
    # Non positive Id
    with pytest.raises(ValueError, match="Card Id must be a positive integer"):
        dao.update(-1, {"name": "Test"})
    cursor.execute.assert_called()


def test_delete(mock_card_dao):
    """Test deleting a card with various scenarios."""
    dao, cursor = mock_card_dao
    result = dao.delete(420)
    assert result is True
    # Non-existent card
    result_false = dao.delete(999)
    assert result_false is False
    # Invalid Id type
    with pytest.raises(TypeError, match="Card Id must be an integer"):
        dao.delete("abc")
    # Non positive Id
    with pytest.raises(ValueError, match="Card Id must be a positive integer"):
        dao.delete(-1)
    cursor.execute.assert_called()
