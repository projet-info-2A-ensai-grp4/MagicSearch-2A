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

# TODO: test generate_text_to_embed2 (Lina?)