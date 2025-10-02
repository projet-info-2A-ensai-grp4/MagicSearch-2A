import pytest
from unittest.mock import MagicMock
from dao.cardDao import CardDao

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")
# Used to warn user that None was returned#
#  (in case the card is non existent)#


@pytest.fixture
def mock_card_dao():
    """
    Mocked DAO fixture for testing without a real database.
    Simulates a single card record with id=420.
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
        "raw": '{"rarity": "rare", "artist": "John Doe"}'
    }
    dao = CardDao()

    def exist_side_effect(card_id):
        if not isinstance(card_id, int):
            raise TypeError("Card ID must be an integer")
        if card_id == 420:
            return True           # card exists
        if card_id < 0:
            raise ValueError("Id must be a positive integer")
        if card_id == 999:
            return False

    def get_by_id_effect(card_id):
        if not isinstance(card_id, int):
            raise TypeError("Card Id must be an integer")
        if card_id == 420:
            return fake_card         # card exists
        if card_id < 0:
            raise ValueError("Card Id must be a positive integer")
        if card_id == 999:
            return None

    def create_effect(card_data):
        if not isinstance(card_data, dict):
            raise TypeError("Card data must be a dictionary")
        if card_data.get("id") == 420:
            raise Exception("Card with this Id already exists")
        if card_data.get("id") < 0:
            raise ValueError("Card Id must be a positive integer")
        if not isinstance(card_data.get("id"), int):
            raise TypeError("Card Id must be an integer")
        return card_data

    def update_effect(card_id, update_data):
        if not isinstance(card_id, int):
            raise TypeError("Card Id must be an integer")
        if not isinstance(update_data, dict):
            raise TypeError("Update data must be a dictionary")
        if card_id == 420:
            updated_card = fake_card.copy()
            updated_card.update(update_data)
            return updated_card
        if card_id < 0:
            raise ValueError("Card Id must be a positive integer")
        return None

    def delete_effect(card_id):
        if not isinstance(card_id, int):
            raise TypeError("Card Id must be an integer")
        if card_id == 420:
            return True
        if card_id < 0:
            raise ValueError("Card Id must be a positive integer")
        return False

    dao.exist.side_effect = exist_side_effect
    dao.get_by_id.side_effect = get_by_id_effect
    dao.create.side_effect = create_effect
    dao.update.side_effect = update_effect
    dao.delete.side_effect = delete_effect
    return dao


def test_exist(mock_card_dao):
    """Test if a card exist with its id """
    result_True = mock_card_dao.exist(420)
    result_False = mock_card_dao.exist(999)
    assert result_True is True
    assert result_False is False
    with pytest.raises(ValueError, match="Id must be a positive integer"):
        mock_card_dao.exist(-1)
    with pytest.raises(TypeError, match="Card ID must be an integer"):
        mock_card_dao.exist("A")


def test_get_by_id(mock_card_dao):
    """Test fetching a card by ID."""
    card = mock_card_dao.get_by_id(420)
    card_none = mock_card_dao.get_by_id(999)
    assert card is not None
    assert card["id"] == 420
    assert card["name"] == "Example Card"
    # Non-existent Card
    assert card_none is None
    # Unvalide id
    with pytest.raises(TypeError, match="Card Id must be an integer"):
        mock_card_dao.get_by_id("")
    with pytest.raises(ValueError, match="Card Id must be a positive integer"):
        mock_card_dao.get_by_id(-1)


def test_create(mock_card_dao):
    """ Test creating a card with a samble of items """
    new_card = {"id": 421, "name": "New Card"}
    created_card = mock_card_dao.create(new_card)
    assert created_card["id"] == 421
    assert created_card["name"] == "New Card"
    # Unvalid type of new_card
    with pytest.raises(TypeError, match="Card data must be a dictionary"):
        mock_card_dao.create("not a dict")
    # unvalid id type
    with pytest.raises(TypeError, match="Card Id must be an integer"):
        mock_card_dao.create({"id": "a", "name": "Duplicate Card"})
    # Duplicate case
    with pytest.raises(Exception, match="Card with this Id already exists"):
        mock_card_dao.create({"id": 420, "name": "Duplicate Card"})
    # id non-negative
    with pytest.raises(ValueError, match="Card Id must be a positive integer"):
        mock_card_dao.create({"id": -1, "name": "Duplicate Card"})


def test_update(mock_card_dao):
    """ Test updating a card, with Id and items who should be change """
    updated_data = {"name": "Updated Card"}
    updated_card = mock_card_dao.update(420, updated_data)
    assert updated_card["id"] == 420
    assert updated_card["name"] == "Updated Card"
    # Non-existent card
    result_none = mock_card_dao.update(999, {"name": "No Card"})
    assert result_none is None
    # Invalid Id
    with pytest.raises(TypeError, match="Card Id must be an integer"):
        mock_card_dao.update("abc", {"name": "Test"})
    # Invalid update data
    with pytest.raises(TypeError, match="Update data must be a dictionary"):
        mock_card_dao.update(420, "not a dict")
    # Non positive Id
    with pytest.raises(ValueError, match="Card Id must be a positive integer"):
        mock_card_dao.update(-1, {"name": "Test"})


def test_delete(mock_card_dao):
    """Test deleting a card with various scenarios."""
    result = mock_card_dao.delete(420)
    assert result is True
    # Non-existent card
    result_false = mock_card_dao.delete(999)
    assert result_false is False
    # Invalid Id type
    with pytest.raises(TypeError, match="Card Id must be an integer"):
        mock_card_dao.delete("abc")
    # Non positive Id
    with pytest.raises(ValueError, match="Card Id must be a positive integer"):
        mock_card_dao.delete(-1)
