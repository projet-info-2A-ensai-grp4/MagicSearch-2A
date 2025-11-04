import pytest
from unittest.mock import MagicMock, patch
from dao.cardDao import CardDao
from services.embeddingService import EmbeddingService
from business_object.cardBusiness import CardBusiness

@pytest.fixture
def mock_dao():
    dao = MagicMock(spec=CardDao)
    dao.get_by_id.return_value = {
        "id": 421,
        "name": "Test Card",
        "type": "Creature",
        "text": "Test description",
        "mana_cost": "{1}{R}",
        "mana_value": 2,
        "power": "2",
        "toughness": "2",
        "color_identity": ["R"],
        "keywords": ["Haste"]
    }
    return dao

@pytest.fixture
def mock_embedding_service():
    service = MagicMock(spec=EmbeddingService)
    service.vectorize.return_value = [0.1, 0.2, 0.3]
    return service

def test_generate_text_to_embed2(mock_dao, mock_embedding_service):
    business = CardBusiness(mock_dao, 421, mock_embedding_service)
    result = business.generate_text_to_embed2()
    assert "Test Card" in result
    assert "Creature" in result
    assert mock_dao.edit_text_to_embed.called

def test_vectorize_success(mock_dao, mock_embedding_service):
    business = CardBusiness(mock_dao, 421, mock_embedding_service)
    business.text_to_embed = "Test text to embed"
    result = business.vectorize()
    assert result == [0.1, 0.2, 0.3]
    assert mock_dao.edit_vector.called

def test_vectorize_no_text():
    dao = MagicMock(spec=CardDao)
    dao.get_by_id.return_value = {"id": 421}
    business = CardBusiness(dao, 421)
    with pytest.raises(AttributeError, match="'CardBusiness' object has no attribute 'text_to_embed'"):
        business.vectorize()

def test_vectorize_api_error(mock_dao, mock_embedding_service):
    mock_embedding_service.vectorize.side_effect = Exception("API Error")
    business = CardBusiness(mock_dao, 421, mock_embedding_service)
    business.text_to_embed = "Test text to embed"
    with pytest.raises(Exception, match="API Error"):
        business.vectorize()
