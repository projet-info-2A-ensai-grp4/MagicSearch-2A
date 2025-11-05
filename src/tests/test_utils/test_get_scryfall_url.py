from unittest.mock import patch, MagicMock
import pytest
from utils.get_scryfall_url import get_card_image_url, fetch_and_update_images


def test_get_card_image_url_success():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "data": [{"image_uris": {"normal": "https://fakeurl.com/card.jpg"}}]
    }

    with patch("requests.get", return_value=fake_response):
        url = get_card_image_url("fake-id")
        assert url == "https://fakeurl.com/card.jpg"


def test_get_card_image_url_no_card():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"data": []}

    with patch("requests.get", return_value=fake_response):
        url = get_card_image_url("fake-id")
        assert url is None


def test_get_card_image_url_api_error():
    fake_response = MagicMock()
    fake_response.status_code = 500

    with patch("requests.get", return_value=fake_response):
        url = get_card_image_url("fake-id")
        assert url is None


def test_fetch_and_update_images():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        {"id": 1, "scryfall_oracle_id": "valid-id"},
        {"id": 2, "scryfall_oracle_id": "no-image-id"},
    ]


def mock_get(url):
    mock_resp = MagicMock()
    if "valid-id" in url:
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": [{"image_uris": {"normal": "https://fakeurl.com/card.jpg"}}]}
    else:
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": []}
    return mock_resp

    with patch("psycopg2.connect", return_value=mock_conn), patch("requests.get", side_effect=mock_get):
        fetch_and_update_images()
        # Vérifie que UPDATE a été appelé pour la première carte
        mock_cursor.execute.assert_any_call(
            "UPDATE cards\n                        SET image_url = %s\n                        WHERE id = %s;",
            ("https://fakeurl.com/card.jpg", 1)
        )


if __name__ == "__main__":
    pytest.main([__file__])
