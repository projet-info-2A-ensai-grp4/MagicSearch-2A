import pytest
from dao.cardDao import CardDao

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning") # Used to warn user that None was returned (in case the card is non existent)


@pytest.fixture
def card_dao():
    """Fixture to provide a CardDao instance for testing."""
    with CardDao() as dao:
        yield dao


def test_get_card_by_id(card_dao):
    """Test fetching a card by ID."""
    test_card_id = 420
    result = card_dao.get_card_by_id(test_card_id)

    # Assert the result matches expectations
    assert result is not None, "No card found"
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result["id"] == test_card_id, "Card ID does not match"
    assert "text_to_embed" in result, "text_to_embed field is missing"


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
    assert updated_card["text_to_embed"] == test_text, (
        "text_to_embed was not updated correctly"
    )


def test_edit_text_to_embed_nonexistent(card_dao):
    """Test editing the text_to_embed value for a non-existent card ID."""
    test_text = "This is a sample text to embed"
    nonexistent_card_id = 99999

    with pytest.raises(
        ValueError, match=f"No card found with ID {nonexistent_card_id}"
    ):
        card_dao.edit_text_to_embed(test_text, nonexistent_card_id)


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
