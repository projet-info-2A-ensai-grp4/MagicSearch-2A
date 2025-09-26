import pytest
import sqlite3
from dao.cardDao import CardDao

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")
# Used to warn user that None was returned#
#  (in case the card is non existent)#


@pytest.fixture
def card_dao():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    card_key VARCHAR,
    name VARCHAR,
    ascii_name VARCHAR,
    text TEXT,
    type VARCHAR,
    layout VARCHAR,
    mana_cost VARCHAR,
    mana_value INT,
    converted_mana_cost INT,
    face_converted_mana_cost INT,
    face_mana_value INT,
    face_name VARCHAR,
    first_printing DATE,
    hand VARCHAR,
    life VARCHAR,
    loyalty VARCHAR,
    power VARCHAR,
    toughness VARCHAR,
    side VARCHAR,
    defense VARCHAR,
    edhrec_rank INT,
    edhrec_saltiness FLOAT,
    is_funny BOOLEAN,
    is_game_changer BOOLEAN,
    is_reserved BOOLEAN,
    has_alternative_deck_limit BOOLEAN,
    colors VARCHAR,
    color_identity VARCHAR,
    color_indicator VARCHAR,
    types VARCHAR,
    subtypes VARCHAR,
    supertypes VARCHAR,
    keywords VARCHAR,
    subsets VARCHAR,
    printings VARCHAR,
    scryfall_oracle_id UUID,
    text_to_embed TEXT,
    embedding VECTOR,   -- requires pgvector extension
    raw JSON);
    INSERT INTO cards (
    id,
    card_key,
    name,
    ascii_name,
    text,
    type,
    layout,
    mana_cost,
    mana_value,
    converted_mana_cost,
    face_converted_mana_cost,
    face_mana_value,
    face_name,
    first_printing,
    hand,
    life,
    loyalty,
    power,
    toughness,
    side,
    defense,
    edhrec_rank,
    edhrec_saltiness,
    is_funny,
    is_game_changer,
    is_reserved,
    has_alternative_deck_limit,
    colors,
    color_identity,
    color_indicator,
    types,
    subtypes,
    supertypes,
    keywords,
    subsets,
    printings,
    scryfall_oracle_id,
    text_to_embed,
    embedding,
    raw
) VALUES (
    420,
    'example_key',
    'Example Card',
    'Example Card',
    'This is an example text for the card.',
    'Creature',
    'normal',
    '{1}{G}',
    2,
    2,
    0,
    0,
    NULL,
    '2020-01-01',
    NULL,
    NULL,
    NULL,
    '2',
    '2',
    NULL,
    NULL,
    1234,
    0.5,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    'G',
    'G',
    NULL,
    'Creature',
    'Elf Druid',
    NULL,
    'Trample',
    NULL,
    'SET1',
    '550e8400-e29b-41d4-a716-446655440000',
    'Some text to embed',
    '[0.1, 0.2, 0.3]', -- embedding vector, pgvector accepts array literal
    '{"rarity": "rare", "artist": "John Doe"}');
    """)
    conn.commit()
    yield conn
    conn.close()


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
