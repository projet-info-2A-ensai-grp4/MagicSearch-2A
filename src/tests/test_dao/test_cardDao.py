import pytest
from unittest.mock import MagicMock, patch
from dao.cardDao import CardDao
import copy

pytestmark = pytest.mark.filterwarnings(
    "ignore::UserWarning"
)  # Used to warn user that None was returned (in case the card is non existent)


@pytest.fixture
def mock_card_dao():
    """Provides a CardDao instance with mocked database interactions."""
    base_card = {
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
        "embedding": [0.1, 0.2, 0.3],
        "raw": '{"rarity": "rare", "artist": "John Doe"}',
    }

    fake_db = {420: copy.deepcopy(base_card)}
    next_id = [421]

    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Context manager support
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_cursor.execute.return_value = None

        # fetchall returns deep copies to avoid mutation issues
        mock_cursor.fetchall.side_effect = lambda: [
            copy.deepcopy(v) for v in fake_db.values()
        ]

        dao = CardDao()
        dao.conn = mock_conn
        dao.cursor = mock_cursor

        # fetchone side effect
        def fetchone_side_effect(*args, **kwargs):
            if not mock_cursor.execute.call_args:
                return None
            sql = mock_cursor.execute.call_args[0][0].strip().upper()
            params = (
                mock_cursor.execute.call_args[0][1]
                if len(mock_cursor.execute.call_args[0]) > 1
                else None
            )

            # COUNT(*)
            if "COUNT(*)" in sql:
                return {"count": len(fake_db)}

            # SELECT BY ID
            if sql.startswith("SELECT") and "WHERE ID = %S" in sql:
                card_id = params[0]
                return copy.deepcopy(fake_db.get(card_id))

            # INSERT
            if sql.startswith("INSERT"):
                card_data = {k: None for k in dao.columns_valid if k != "id"}
                if params:
                    for i, key in enumerate(card_data.keys()):
                        if i < len(params):
                            card_data[key] = params[i]
                card_data["id"] = next_id[0]
                next_id[0] += 1
                fake_db[card_data["id"]] = copy.deepcopy(card_data)
                return copy.deepcopy(card_data)

            # UPDATE
            if sql.startswith("UPDATE"):
                if not params:
                    return None
                card_id = params[-1]
                if card_id in fake_db:
                    set_part = sql.split("SET")[1].split("WHERE")[0]
                    cols = [
                        p.split("=")[0].strip().lower() for p in set_part.split(",")
                    ]
                    values = params[:-1]
                    for col, val in zip(cols, values):
                        fake_db[card_id][col] = val
                    return copy.deepcopy(fake_db[card_id])
                return None

            # DELETE
            if sql.startswith("DELETE"):
                card_id = params[0]
                return copy.deepcopy(fake_db.pop(card_id, None))

            return None

        mock_cursor.fetchone.side_effect = fetchone_side_effect

        yield dao, mock_cursor, fake_db


# -----------------------
# Tests
# -----------------------


def test_shape(mock_card_dao):
    dao, mock_cursor, fake_db = mock_card_dao
    row_count, col_count = dao.shape()
    assert row_count == len(fake_db)
    assert col_count == len(dao.columns_valid)
    mock_cursor.execute.assert_called()
    assert "COUNT(*)" in mock_cursor.execute.call_args[0][0].upper()
    mock_cursor.fetchone.assert_called_once()


def test_exist(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    assert dao.exist(420) is True
    assert dao.exist(999) is False
    with pytest.raises(ValueError):
        dao.exist(-1)
    with pytest.raises(TypeError):
        dao.exist("A")
    cursor.execute.assert_called()


def test_get_by_id(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    card = dao.get_by_id(420)
    assert card is not None
    assert card["id"] == 420
    assert dao.get_by_id(999) is None
    with pytest.raises(TypeError):
        dao.get_by_id("")
    with pytest.raises(ValueError):
        dao.get_by_id(-1)
    cursor.execute.assert_called()


def test_create(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    created_card = dao.create(name="New Card", type="Spell", mana_value=1)
    assert created_card["id"] in fake_db
    assert created_card["name"] == "New Card"
    assert created_card["type"] == "Spell"
    assert created_card["mana_value"] == 1
    with pytest.raises(ValueError):
        dao.create(nonexistent_column="Oops")


def test_update(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    updated_card = dao.update(420, name="Updated Card")
    assert updated_card["name"] == "Updated Card"
    assert dao.update(999, {"name": "No Card"}) is None
    with pytest.raises(TypeError):
        dao.update("abc", {"name": "Test"})
    with pytest.raises(ValueError):
        dao.update(-1, name="Updated Card")
    cursor.execute.assert_called()


def test_delete(mock_card_dao):
    dao, cursor, fake_db = mock_card_dao
    result = dao.delete(420)
    assert result["name"] == "Example Card"
    assert dao.exist(420) is False
    assert dao.delete(999) is None
    with pytest.raises(TypeError):
        dao.delete("abc")
    with pytest.raises(ValueError):
        dao.delete(-1)
    cursor.execute.assert_called()


def test_filter_with_valid_kwargs(mock_card_dao):
    dao, mock_cursor, fake_db = mock_card_dao

    # Ajouter une seconde carte pour tester le filtrage
    fake_db[421] = copy.deepcopy(fake_db[420])
    fake_db[421]["id"] = 421
    fake_db[421]["name"] = "Other Card"
    fake_db[421]["type"] = "Artifact"

    # Mock le retour de fetchall pour filtrer correctement par type
    mock_cursor.fetchall.side_effect = lambda: [
        card for card in fake_db.values() if card["type"] == "Creature"
    ]

    results = dao.filter(order_by="id", type="Creature")
    query, params = mock_cursor.execute.call_args[0]

    # Vérifications de la requête SQL
    assert "SELECT * FROM cards" in query
    assert "WHERE TRUE AND type = %s" in query
    assert "ORDER BY id ASC" in query
    assert "LIMIT %s OFFSET %s" in query
    assert params[:-2] == ["Creature"]
    assert params[-2:] == [100, 0]

    # Vérification des résultats filtrés
    assert all(r["type"] == "Creature" for r in results)
    assert [r["id"] for r in results] == [420]  # seul l'id 420 correspond au filtre
