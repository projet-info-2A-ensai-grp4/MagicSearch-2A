import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open, call
import os
import sys
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from add_img import (
    get_last_processed_id,
    save_progress,
    get_card_image_url,
    fetch_and_update_images,
    PROGRESS_FILE,
)


# Tests for get_last_processed_id()
def test_get_last_processed_id_file_exists():
    mock_file_content = "42"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_last_processed_id()

    assert result == 42


def test_get_last_processed_id_file_not_exists():
    with patch("os.path.exists", return_value=False):
        result = get_last_processed_id()

    assert result == 0


def test_get_last_processed_id_empty_file():
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="")):
            with pytest.raises(ValueError):
                get_last_processed_id()


# Tests for save_progress()
def test_save_progress():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        save_progress(123)

    mock_file.assert_called_once_with(PROGRESS_FILE, "w")
    mock_file().write.assert_called_once_with("123")


def test_save_progress_zero():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        save_progress(0)

    mock_file().write.assert_called_once_with("0")


# Tests for get_card_image_url()
def test_get_card_image_url_single_faced_card():
    oracle_id = "test-oracle-id"
    expected_url = "https://example.com/card.jpg"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"image_uris": {"normal": expected_url}}]
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = get_card_image_url(oracle_id)

    assert result == expected_url
    mock_get.assert_called_once_with(
        f"https://api.scryfall.com/cards/search?q=oracleid:{oracle_id}", timeout=10
    )


def test_get_card_image_url_multi_faced_card():
    oracle_id = "multi-face-oracle-id"
    expected_url = "https://example.com/card_front.jpg"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "card_faces": [
                    {"image_uris": {"normal": expected_url}},
                    {"image_uris": {"normal": "https://example.com/card_back.jpg"}},
                ]
            }
        ]
    }

    with patch("requests.get", return_value=mock_response):
        result = get_card_image_url(oracle_id)

    assert result == expected_url


def test_get_card_image_url_api_error():
    oracle_id = "error-oracle-id"

    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        result = get_card_image_url(oracle_id)

    assert result is None


def test_get_card_image_url_no_data():
    oracle_id = "no-data-oracle-id"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}

    with patch("requests.get", return_value=mock_response):
        result = get_card_image_url(oracle_id)

    assert result is None


def test_get_card_image_url_connection_error():
    oracle_id = "connection-error-id"

    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Connection failed"),
    ):
        result = get_card_image_url(oracle_id)

    assert result is None


def test_get_card_image_url_timeout():
    oracle_id = "timeout-oracle-id"

    with patch(
        "requests.get", side_effect=requests.exceptions.Timeout("Request timeout")
    ):
        result = get_card_image_url(oracle_id)

    assert result is None


def test_get_card_image_url_no_image_uris():
    oracle_id = "no-image-oracle-id"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{}]}

    with patch("requests.get", return_value=mock_response):
        result = get_card_image_url(oracle_id)

    assert result is None


# Tests for fetch_and_update_images()
@patch("add_img.get_last_processed_id")
@patch("add_img.save_progress")
@patch("add_img.get_card_image_url")
@patch("add_img.psycopg2.connect")
@patch("add_img.load_dotenv")
@patch("os.getenv")
@patch("os.path.exists")
@patch("os.remove")
@patch("time.sleep")
def test_fetch_and_update_images_success(
    mock_sleep,
    mock_remove,
    mock_exists,
    mock_getenv,
    mock_load_dotenv,
    mock_connect,
    mock_get_image,
    mock_save_progress,
    mock_get_last_id,
):
    # Setup mocks
    mock_get_last_id.return_value = 0
    mock_getenv.side_effect = lambda key, default=None: {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
    }.get(key, default)

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "scryfall_oracle_id": "oracle-1", "name": "Card 1"},
        {"id": 2, "scryfall_oracle_id": "oracle-2", "name": "Card 2"},
    ]

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    mock_get_image.side_effect = ["http://image1.jpg", "http://image2.jpg"]
    mock_exists.return_value = True

    fetch_and_update_images()

    assert mock_cursor.execute.call_count == 3  # 1 SELECT + 2 UPDATEs
    assert mock_save_progress.call_count == 2
    mock_save_progress.assert_any_call(1)
    mock_save_progress.assert_any_call(2)
    mock_remove.assert_called_once_with(PROGRESS_FILE)


@patch("add_img.get_last_processed_id")
@patch("add_img.save_progress")
@patch("add_img.get_card_image_url")
@patch("add_img.psycopg2.connect")
@patch("add_img.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_fetch_and_update_images_resume_from_progress(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_connect,
    mock_get_image,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 50
    mock_getenv.side_effect = lambda key, default=None: {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
    }.get(key, default)

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    fetch_and_update_images()

    # Verify it queried for cards with id > 50
    select_call = mock_cursor.execute.call_args_list[0]
    assert select_call[0][1] == (50,)


@patch("add_img.get_last_processed_id")
@patch("add_img.save_progress")
@patch("add_img.get_card_image_url")
@patch("add_img.psycopg2.connect")
@patch("add_img.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_fetch_and_update_images_no_image_found(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_connect,
    mock_get_image,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    mock_getenv.side_effect = lambda key, default=None: {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
    }.get(key, default)

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "scryfall_oracle_id": "oracle-1", "name": "Card 1"}
    ]

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    mock_get_image.return_value = None

    fetch_and_update_images()

    # Should still save progress even when image not found
    mock_save_progress.assert_called_once_with(1)
    # Should only have 1 execute call (SELECT), no UPDATE
    assert mock_cursor.execute.call_count == 1


@patch("add_img.get_last_processed_id")
@patch("add_img.psycopg2.connect")
@patch("add_img.load_dotenv")
@patch("os.getenv")
def test_fetch_and_update_images_keyboard_interrupt(
    mock_getenv, mock_load_dotenv, mock_connect, mock_get_last_id
):
    mock_get_last_id.return_value = 0
    mock_getenv.side_effect = lambda key, default=None: {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
    }.get(key, default)

    mock_connect.side_effect = KeyboardInterrupt()

    # Should handle KeyboardInterrupt gracefully
    fetch_and_update_images()


@patch("add_img.get_last_processed_id")
@patch("add_img.psycopg2.connect")
@patch("add_img.load_dotenv")
@patch("os.getenv")
def test_fetch_and_update_images_database_error(
    mock_getenv, mock_load_dotenv, mock_connect, mock_get_last_id
):
    mock_get_last_id.return_value = 0
    mock_getenv.side_effect = lambda key, default=None: {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
    }.get(key, default)

    mock_connect.side_effect = Exception("Database connection failed")

    with pytest.raises(Exception, match="Database connection failed"):
        fetch_and_update_images()
