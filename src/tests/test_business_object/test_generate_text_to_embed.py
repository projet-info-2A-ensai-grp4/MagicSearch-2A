import re
import pytest
from unittest.mock import patch
from business_object.cardBusiness import CardBusiness
from dao.cardDao import CardDao


MOCK = {
    "id": 420,
    "name": "Mock Card",
    "type": "Creature - Elf",
    "text": "When this card enters the battlefield, draw a card.",
    "mana_cost": "{2}{G}",
    "mana_value": 3,
    "power": "2",
    "toughness": "2",
    "color_identity": ["G"],
    "keywords": ["Trample"],
}


@patch("card_business_module.CardDao")
def test_generate_text_to_embed2(MockDao):
    mock_dao_instance = MockDao.return_value
    mock_dao_context = mock_dao_instance.__enter__.return_value

    mock_dao_context.get_by_id.return_value = MOCK.copy()

    mock_dao_context.edit_text_to_embed.return_value = 1

    b = card_business_module.CardBusiness(mock_dao_instance, 420)

    result = b.generate_text_to_embed2()

    assert re.search(re.escape(MOCK["name"]), result)
    assert re.search(re.escape(MOCK["type"]), result)
    assert re.search(re.escape(MOCK["text"]), result)
    assert re.search(re.escape(MOCK["mana_cost"]), result)
    assert re.search(str(MOCK["mana_value"]), result)
    for color in MOCK["color_identity"]:
        assert re.search(re.escape(color), result)
    for keyword in MOCK["keywords"]:
        assert re.search(re.escape(keyword), result)

    mock_dao_context.edit_text_to_embed.assert_called_once_with(result, 420)

    assert b.text_to_embed == result
