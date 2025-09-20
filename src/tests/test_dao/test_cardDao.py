import pytest
from dao.cardDao import CardDao


@pytest.fixture
def card_dao():
    """Fixture to provide a CardDao instance for testing."""
    with CardDao() as dao:
        yield dao  # Passes the dao to the test function


def test_get_card_by_id(card_dao):
    """Test fetching a card by ID."""
    test_card_id = 420  # id of a card
    result = card_dao.get_card_by_id(test_card_id)

    # Assert the result matches expectations
    assert result is not None
    assert result["id"] == test_card_id


def test_edit_text_to_embed(card_dao):
    "Test editing the text_to_embed value"
    test_text = "This is a sample text to embed"
    test_card_id = 420
    result = card_dao.edit_text_to_embed(test_text, test_card_id)

    assert result == 1
    assert card_dao.get_card_by_id(test_card_id)["text_to_embed"] == test_text
