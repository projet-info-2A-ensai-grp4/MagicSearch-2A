import pytest
from unittest.mock import MagicMock
from business_object.favoriteBusiness import FavoriteBusiness


@pytest.fixture
def mock_favorite_business():
    mock_user_dao = MagicMock()
    mock_card_dao = MagicMock()
    mock_favorites_dao = MagicMock()

    mock_user_dao.exist.return_value = True
    mock_card_dao.exist.return_value = True
    mock_favorites_dao.exist.return_value = False

    mock_favorites_dao.create.return_value = {
        "user_id": 1,
        "card_id": 42,
        "added_at": "2025-11-03 12:00:00",
    }
    mock_favorites_dao.delete.return_value = {
        "user_id": 1,
        "card_id": 42,
    }

    fav_business = FavoriteBusiness(
        mock_favorites_dao, mock_user_dao, mock_card_dao
    )
    return fav_business, mock_user_dao, mock_card_dao, mock_favorites_dao


def test_ass_favorite_success(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business

    result = fav.add_favorite(1, 42)

    fav_dao.create.assert_called_once_with(1, 42)
    assert result["user_id"] == 1
    assert result["card_id"] == 42


def test_add_favorite_existing(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    fav_dao.exist.return_value = True

    result = fav.add_favorite(1, 42)

    fav_dao.create.assert_not_called()
    assert result == {"user_id": 1, "card_id": 42}


def test_add_favorite_invalid_user(mock_favorite_business): 
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    user_dao.exist.return_value = False

    with pytest.raises(ValueError, match="user_id"):
        fav.add_favorite(999, 42)

    fav_dao.create.assert_not_called()


def test_add_favorite_invalid_card(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    card_dao.exist.return_value = False

    with pytest.raises(ValueError, match="card_id"):
        fav.add_favorite(1, 999)

    fav_dao.create.assert_not_called()


def test_remove_favorite_success(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    fav_dao.exist.return_value = True

    result = fav.remove_favorite(1, 42)

    fav_dao.delete.assert_called_once_with([1, 42])
    assert result == {"user_id": 1, "card_id": 42}


def test_remove_favorite_not_exist(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    fav_dao.exist.return_value = False

    with pytest.raises(ValueError, match="favorite_id"):
        fav.remove_favorite(1, 42)


def test_remove_favorite_invalid_user(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    user_dao.exist.return_value = False

    with pytest.raises(ValueError, match="user_id"):
        fav.remove_favorite(999, 42)

   
def test_remove_favorite_invalid_card(mock_favorite_business):
    fav, user_dao, card_dao, fav_dao = mock_favorite_business
    card_dao.exist.return_value = False

    with pytest.raises(ValueError, match="card_id"):
        fav.remove_favorite(1, 999)


