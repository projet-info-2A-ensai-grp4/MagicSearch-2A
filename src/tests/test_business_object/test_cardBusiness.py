import pytest
from unittest.mock import Mock, MagicMock, patch
from business_object.cardBusiness import CardBusiness
from dao.cardDao import CardDao
from services.embeddingService import EmbeddingService


def create_mock_card_data(card_id=1, **overrides):
    """Helper function to create complete mock card data with all attributes."""
    default_data = {
        "id": card_id,
        "card_key": f"card_key_{card_id}",
        "name": "Test Card",
        "ascii_name": "Test Card",
        "text": None,
        "type": None,
        "layout": "normal",
        "mana_cost": None,
        "mana_value": None,
        "converted_mana_cost": None,
        "face_converted_mana_cost": None,
        "face_mana_value": None,
        "face_name": None,
        "first_printing": None,
        "hand": None,
        "life": None,
        "loyalty": None,
        "power": None,
        "toughness": None,
        "side": None,
        "defense": None,
        "edhrec_rank": None,
        "edhrec_saltiness": None,
        "is_funny": False,
        "is_game_changer": False,
        "is_reserved": False,
        "has_alternative_deck_limit": False,
        "colors": None,
        "color_identity": None,
        "color_indicator": None,
        "types": None,
        "subtypes": None,
        "supertypes": None,
        "keywords": None,
        "subsets": None,
        "printings": None,
        "scryfall_oracle_id": None,
        "text_to_embed": None,
        "embedding": None,
        "image_url": None,
        "raw": None,
    }
    default_data.update(overrides)
    return default_data


# Tests __init__()
def test_init_valid_card():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        1,
        name="Lightning Bolt",
        type="Instant",
        text="Deal 3 damage to any target.",
    )

    card = CardBusiness(mock_dao, 1)

    assert card.id == 1
    assert card.name == "Lightning Bolt"
    assert card.type == "Instant"
    assert card.text == "Deal 3 damage to any target."
    mock_dao.get_by_id.assert_called_once_with(1)


def test_init_card_not_found():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Card with ID 999 does not exist."):
        CardBusiness(mock_dao, 999)


def test_init_with_custom_embedding_service():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(1, name="Test Card")
    mock_embedding_service = Mock(spec=EmbeddingService)

    card = CardBusiness(mock_dao, 1, embedding_service=mock_embedding_service)

    assert card.embedding_service == mock_embedding_service


# Tests generate_text_to_embed2()
def test_generate_text_to_embed2_basic():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        1,
        name="Lightning Bolt",
        type="Instant",
        text="Deal 3 damage to any target.",
    )
    mock_dao.edit_text_to_embed = Mock()

    card = CardBusiness(mock_dao, 1)
    result = card.generate_text_to_embed2()

    assert "Card: Lightning Bolt" in result
    assert "Type: Instant" in result
    assert "Rules text: Deal 3 damage to any target." in result
    assert result.endswith(".")
    mock_dao.edit_text_to_embed.assert_called_once()


def test_generate_text_to_embed2_full_attributes():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        2,
        name="Tarmogoyf",
        type="Creature — Lhurgoyf",
        types="Creature",
        subtypes="Lhurgoyf",
        mana_cost="{1}{G}",
        mana_value=2,
        colors="Green",
        color_identity="G",
        text="Tarmogoyf's power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.",
        power="*",
        toughness="1+*",
        layout="normal",
    )
    mock_dao.edit_text_to_embed = Mock()

    card = CardBusiness(mock_dao, 2)
    result = card.generate_text_to_embed2()

    assert "Card: Tarmogoyf" in result
    assert "Mana cost: {1}{G}" in result
    assert "Colors: Green" in result
    assert "Power/Toughness: *" in result
    mock_dao.edit_text_to_embed.assert_called_once()


def test_generate_text_to_embed2_no_id():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(1, name="Test Card")

    card = CardBusiness(mock_dao, 1)
    card.id = None

    with pytest.raises(ValueError, match="Impossible to generate text_to_embed without a card ID."):
        card.generate_text_to_embed2()


def test_generate_text_to_embed2_special_properties():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        3,
        name="Black Lotus",
        type="Artifact",
        is_reserved=True,
    )
    mock_dao.edit_text_to_embed = Mock()

    card = CardBusiness(mock_dao, 3)
    result = card.generate_text_to_embed2()

    assert "Reserved List card" in result


def test_generate_text_to_embed2_keywords():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        4,
        name="Serra Angel",
        type="Creature",
        keywords="Flying, Vigilance",
    )
    mock_dao.edit_text_to_embed = Mock()

    card = CardBusiness(mock_dao, 4)
    result = card.generate_text_to_embed2()

    assert "Keywords: Flying, Vigilance" in result


# Tests vectorize()
def test_vectorize_with_text_parameter():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(1, name="Test Card")
    mock_dao.edit_vector = Mock()

    mock_embedding_service = Mock(spec=EmbeddingService)
    mock_embedding_service.vectorize.return_value = [0.1, 0.2, 0.3]

    card = CardBusiness(mock_dao, 1, embedding_service=mock_embedding_service)
    result = card.vectorize(text="Custom text to vectorize")

    assert result == [0.1, 0.2, 0.3]
    assert card.embedding == [0.1, 0.2, 0.3]
    mock_embedding_service.vectorize.assert_called_once_with("Custom text to vectorize")
    mock_dao.edit_vector.assert_called_once_with([0.1, 0.2, 0.3], 1)


def test_vectorize_with_text_to_embed():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        1,
        name="Test Card",
        text_to_embed="Embedded text"
    )
    mock_dao.edit_vector = Mock()

    mock_embedding_service = Mock(spec=EmbeddingService)
    mock_embedding_service.vectorize.return_value = [0.4, 0.5, 0.6]

    card = CardBusiness(mock_dao, 1, embedding_service=mock_embedding_service)
    result = card.vectorize()

    assert result == [0.4, 0.5, 0.6]
    mock_embedding_service.vectorize.assert_called_once_with("Embedded text")


def test_vectorize_no_text_available():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(1, name="Test Card")

    mock_embedding_service = Mock(spec=EmbeddingService)

    card = CardBusiness(mock_dao, 1, embedding_service=mock_embedding_service)

    with pytest.raises(ValueError, match="No text available to vectorize."):
        card.vectorize()


# Tests __repr__()
def test_repr():
    mock_dao = Mock(spec=CardDao)
    mock_dao.__enter__ = Mock(return_value=mock_dao)
    mock_dao.__exit__ = Mock(return_value=False)
    mock_dao.get_by_id.return_value = create_mock_card_data(
        1,
        name="Lightning Bolt",
        type="Instant"
    )

    card = CardBusiness(mock_dao, 1)
    repr_str = repr(card)

    assert "CardBusiness(" in repr_str
    assert "id=1" in repr_str
    assert "name=Lightning Bolt" in repr_str
