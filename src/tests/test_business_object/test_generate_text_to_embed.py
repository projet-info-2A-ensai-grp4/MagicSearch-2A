from unittest.mock import patch
import dao.cardDao as card_dao_module
import business_object.cardBusiness as card_business_module


MOCK = {
    "id": 420,
    "name": "Adarkar Wastes",
    "type": "Land",
    "text": "{T}: Add {C}.",
    "colors": [],  # card without any color information
    "text_to_embed": None,
    "embedding": None,
}


@patch("dao.cardDao.CardDao")
def test_generate_text_to_embed_without_colors(MockDao):
    mock = MockDao.return_value.__enter__.return_value
    mock.get_card_by_id.return_value = MOCK.copy()

    with card_dao_module.CardDao() as dao:
        b = card_business_module.CardBusiness(dao, 420)
        result = b.generate_text_to_embed()

    assert result == "Adarkar Wastes | Land | {T}: Add {C}."
    mock.edit_text_to_embed.assert_called_once_with(result, 420)
    assert b.text_to_embed == result


@patch("dao.cardDao.CardDao")
def test_generate_text_to_embed_with_colors(MockDao):
    mock = MockDao.return_value.__enter__.return_value
    data = MOCK.copy()
    data["colors"] = ["U", "W"]  # card with colors
    mock.get_card_by_id.return_value = data

    with card_dao_module.CardDao() as dao:
        b = card_business_module.CardBusiness(dao, 420)
        result = b.generate_text_to_embed()

    assert result == "Adarkar Wastes | Land | {T}: Add {C}. | U, W"
    mock.edit_text_to_embed.assert_called_once_with(result, 420)
    assert b.text_to_embed == result

# TODO: test generate_text_to_embed2 (Lina?)