import pytest
from unittest.mock import MagicMock, patch
from dao.cardDao import CardDao
from business_object.cardBusiness import CardBusiness  # Replace `your_module` with the actual module name
import os
from dotenv import load_dotenv

pytestmark = pytest.mark.filterwarnings(
    "ignore::UserWarning"
)   # Used to warn user that None was returned (in case the card is non existent)

# Mock data for testing
MOCK_CARD_DATA = {
    "id": 420,
    "card_key": "Adarkar Wastes",
    "name": "Adarkar Wastes",
    "ascii_name": None,
    "text": "{T}: Add {C}.\n{T}: Add {W} or {U}. This land deals 1 damage to you.",
    "type": "Land",
    "layout": "normal",
    "mana_cost": None,
    "mana_value": 0.0,
    "converted_mana_cost": 0.0,
    "face_converted_mana_cost": None,
    "face_mana_value": None,
    "face_name": None,
    "first_printing": "ICE",
    "hand": None,
    "life": None,
    "loyalty": None,
    "power": None,
    "toughness": None,
    "side": None,
    "defense": None,
    "edhrec_rank": 182,
    "edhrec_saltiness": 0.05,
    "is_funny": None,
    "is_game_changer": None,
    "is_reserved": None,
    "has_alternative_deck_limit": None,
    "colors": [],
    "color_identity": ["U", "W"],
    "color_indicator": None,
    "types": ["Land"],
    "subtypes": [],
    "supertypes": [],
    "keywords": None,
    "subsets": None,
    "printings": [
        "10E",
        "5ED",
        "6ED",
        "7ED",
        "9ED",
        "BLC",
        "DMU",
        "DRC",
        "DSC",
        "EOC",
        "ICE",
        "M3C",
        "OLEP",
        "PDMU",
        "PLST",
        "PRM",
        "PTC",
        "TDC",
        "WC00",
    ],
    "scryfall_oracle_id": "d5ad26cc-2bdb-46b7-b8bf-dd099d5fa09b",
    "text_to_embed": "This is a sample text to embed",
    "embedding": None,
    "raw": {
        "name": "Adarkar Wastes",
        "text": "{T}: Add {C}.\n{T}: Add {W} or {U}. This land deals 1 damage to you.",
        "type": "Land",
        "types": ["Land"],
        "colors": [],
        "layout": "normal",
        "subtypes": [],
        "manaValue": 0.0,
        "printings": [
            "10E",
            "5ED",
            "6ED",
            "7ED",
            "9ED",
            "BLC",
            "DMU",
            "DRC",
            "DSC",
            "EOC",
            "ICE",
            "M3C",
            "OLEP",
            "PDMU",
            "PLST",
            "PRM",
            "PTC",
            "TDC",
            "WC00",
        ],
        "edhrecRank": 182,
        "legalities": {
            "duel": "Legal",
            "brawl": "Legal",
            "penny": "Legal",
            "predh": "Legal",
            "legacy": "Legal",
            "modern": "Legal",
            "pioneer": "Legal",
            "vintage": "Legal",
            "historic": "Legal",
            "timeless": "Legal",
            "commander": "Legal",
            "gladiator": "Legal",
            "premodern": "Legal",
            "oathbreaker": "Legal",
        },
        "supertypes": [],
        "foreignData": [
            {
                "name": "Adarkarwüste",
                "text": "{T}: Erhöhe Deinen Manavorrat um ein farbloses Mana.\n{T}: Erhöhe Deinen Manavorrat um {W} oder U. Die Adarkarwüste fügt Dir 1 Schadenspunkt zu.",
                "type": "Land",
                "language": "German",
            },
            {
                "name": "Yermos de Adarkar",
                "language": "Spanish",
            },
            {
                "name": "Landes d'Adarkar",
                "language": "French",
            },
            {
                "name": "Distese dell'Adarkar",
                "language": "Italian",
            },
            {
                "name": "アダーカー荒原",
                "language": "Japanese",
            },
            {
                "name": "Regiões Agrestes de Adarkar",
                "language": "Portuguese (Brazil)",
            },
        ],
        "identifiers": {
            "scryfallOracleId": "d5ad26cc-2bdb-46b7-b8bf-dd099d5fa09b",
        },
        "purchaseUrls": {
            "tcgplayer": "https://mtgjson.com/links/b7aee06cfb6cbcbc",
            "cardKingdom": "https://mtgjson.com/links/bfaf1a80e750861d",
        },
        "colorIdentity": ["U", "W"],
        "firstPrinting": "ICE",
        "edhrecSaltiness": 0.05,
        "convertedManaCost": 0.0,
    },
}


# Fixture to mock CardDao
@pytest.fixture
def mock_card_dao():
    with patch("dao.cardDao.CardDao") as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value.__enter__.return_value = mock_dao
        yield mock_dao


# Fixture to load environment variables for testing
@pytest.fixture(autouse=True)
def load_env():
    # Load environment variables from .env.test if it exists
    load_dotenv(".env.test")


# Test initialization of CardBusiness
def test_card_business_init_success(mock_card_dao):
    """Test initializing CardBusiness with a valid card_id."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    with CardDao() as dao:
        business = CardBusiness(dao, 420)

    assert business.id == 420
    assert business.name == "Adarkar Wastes"
    # assert business.text_to_embed == "This is a sample text to embed"
    # mock_card_dao.get_card_by_id.assert_called_once_with(420)


def test_card_business_init_card_not_found(mock_card_dao):
    """Test initializing CardBusiness with a non-existent card_id."""
    mock_card_dao.get_card_by_id.return_value = None

    with CardDao() as dao:
        with pytest.raises(
            ValueError, match="Card with ID 99999 does not exist."
        ):
            CardBusiness(dao, 99999)


# Test the __repr__ method
def test_card_business_repr(mock_card_dao):
    """Test the string representation of CardBusiness."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    with CardDao() as dao:
        business = CardBusiness(dao, 420)

    assert "id=420, card_key=Adarkar Wastes, name=Adarkar Wastes" in repr(
        business
    )
    assert "text={T}: Add {C}." in repr(business)
    assert "color_identity=['U', 'W']" in repr(business)


# Test the vectorize method
def test_vectorize_success(mock_card_dao, requests_mock):
    """Test successful vectorization of text."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    # Mock the Ollama API response
    mock_embedding = [[0.1, 0.2, 0.3]]
    requests_mock.post(
        "https://llm.lab.sspcloud.fr/ollama/api/embed",
        json={"embeddings": mock_embedding},
        status_code=200,
    )

    with CardDao() as dao:
        business = CardBusiness(dao, 420)
        embedding = business.vectorize(
            business.text_to_embed,
        )

    assert embedding == mock_embedding[0]


def test_vectorize_invalid_response(mock_card_dao, requests_mock):
    """Test vectorization with an invalid API response."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    # Mock an invalid API response
    requests_mock.post(
        "https://llm.lab.sspcloud.fr/ollama/api/embed",
        json={"error": "Invalid request"},
        status_code=200,
    )

    with CardDao() as dao:
        business = CardBusiness(dao, 420)
        with pytest.raises(
            ValueError,
            match="Invalid response format: 'embedding' field not found.",
        ):
            business.vectorize(
                business.text_to_embed,
            )


def test_vectorize_api_error(mock_card_dao, requests_mock):
    """Test vectorization with an API error."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    # Mock an API error
    requests_mock.post(
        "https://llm.lab.sspcloud.fr/ollama/api/embed",
        json={"error": "Internal server error"},
        status_code=500,
    )

    with CardDao() as dao:
        business = CardBusiness(dao, 420)
        with pytest.raises(ValueError, match="Failed to vectorize text:"):
            business.vectorize(
                business.text_to_embed,
            )


# Test the main block
@patch("builtins.print")
@patch("business_object.cardBusiness.load_dotenv")  # nameofthefile.load_dotenv
@patch.dict(os.environ, {"LLM_API_KEY": "test_api_key"})
def test_main_block_success(
    mock_load_dotenv, mock_print, mock_card_dao, requests_mock
):
    """Test the main block with a successful vectorization."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    # Mock the Ollama API response
    mock_embedding = [[0.1, 0.2, 0.3]]
    requests_mock.post(
        "https://llm.lab.sspcloud.fr/ollama/api/embed",
        json={"embeddings": mock_embedding},
        status_code=200,
    )

    # Simulate the main block
    with CardDao() as dao:
        business = CardBusiness(dao, 420)
        embedding = business.vectorize(
            business.text_to_embed,
        )

    assert embedding == mock_embedding[0]


@patch("builtins.print")
@patch("business_object.cardBusiness.load_dotenv")
@patch.dict(os.environ, {"LLM_API_KEY": "test_api_key"})
def test_main_block_error(
    mock_load_dotenv, mock_print, mock_card_dao, requests_mock
):
    """Test the main block with an error during vectorization."""
    mock_card_dao.get_card_by_id.return_value = MOCK_CARD_DATA

    # Mock an API error
    requests_mock.post(
        "https://llm.lab.sspcloud.fr/ollama/api/embed",
        json={"error": "Internal server error"},
        status_code=500,
    )

    # Simulate the main block
    with CardDao() as dao:
        business = CardBusiness(dao, 420)
        with pytest.raises(ValueError, match="Failed to vectorize text:"):
            business.vectorize(
                business.text_to_embed,
            )
