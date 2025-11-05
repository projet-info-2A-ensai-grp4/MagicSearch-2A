import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open, call
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vectorize import (
    get_last_processed_id,
    save_progress,
    process_all_cards,
    PROGRESS_FILE,
)


# Tests for get_last_processed_id()
def test_get_last_processed_id_file_exists():
    mock_file_content = "150"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_last_processed_id()

    assert result == 150


def test_get_last_processed_id_file_not_exists():
    with patch("os.path.exists", return_value=False):
        result = get_last_processed_id()

    assert result == 0


def test_get_last_processed_id_empty_file():
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="")):
            with pytest.raises(ValueError):
                get_last_processed_id()


def test_get_last_processed_id_invalid_content():
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="not_a_number")):
            with pytest.raises(ValueError):
                get_last_processed_id()


# Tests for save_progress()
def test_save_progress():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        save_progress(500)

    mock_file.assert_called_once_with(PROGRESS_FILE, "w")
    mock_file().write.assert_called_once_with("500")


def test_save_progress_zero():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        save_progress(0)

    mock_file().write.assert_called_once_with("0")


def test_save_progress_large_number():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        save_progress(32548)

    mock_file().write.assert_called_once_with("32548")


# Tests for process_all_cards()
@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("os.path.exists")
@patch("os.remove")
@patch("time.sleep")
def test_process_all_cards_success_small_batch(
    mock_sleep,
    mock_remove,
    mock_exists,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    # Setup mocks
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = "test_api_key"
    mock_exists.return_value = True

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.text_to_embed = "test text"
    mock_card_business_class.return_value = mock_business

    # Test with small range
    process_all_cards(max_card_id=3)

    # Verify CardBusiness was called for each card
    assert mock_card_business_class.call_count == 3
    assert mock_business.generate_text_to_embed2.call_count == 3
    assert mock_business.vectorize.call_count == 3
    assert mock_save_progress.call_count == 3
    mock_remove.assert_called_once_with(PROGRESS_FILE)


@patch("vectorize.get_last_processed_id")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
def test_process_all_cards_no_api_key(mock_getenv, mock_load_dotenv, mock_get_last_id):
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = None

    process_all_cards()


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_process_all_cards_resume_from_progress(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    # Resume from card 100
    mock_get_last_id.return_value = 100
    mock_getenv.return_value = "test_api_key"

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.text_to_embed = "test text"
    mock_card_business_class.return_value = mock_business

    process_all_cards(max_card_id=102)

    # Should only process cards 101 and 102
    assert mock_card_business_class.call_count == 2
    mock_card_business_class.assert_any_call(mock_dao, 101)
    mock_card_business_class.assert_any_call(mock_dao, 102)


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_process_all_cards_value_error_continue(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = "test_api_key"

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.text_to_embed = "test text"
    # Raise ValueError on card 2
    mock_business.generate_text_to_embed2.side_effect = [
        None,
        ValueError("Card not found"),
        None,
    ]
    mock_card_business_class.return_value = mock_business

    process_all_cards(max_card_id=3)

    # Should process all 3 cards despite error on card 2
    assert mock_card_business_class.call_count == 3
    assert mock_save_progress.call_count == 3


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_process_all_cards_unexpected_error_raises(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = "test_api_key"

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.generate_text_to_embed2.side_effect = RuntimeError("Database error")
    mock_card_business_class.return_value = mock_business

    with pytest.raises(RuntimeError, match="Database error"):
        process_all_cards(max_card_id=2)


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_process_all_cards_keyboard_interrupt(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = "test_api_key"

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.generate_text_to_embed2.side_effect = [None, KeyboardInterrupt()]
    mock_card_business_class.return_value = mock_business

    # Should handle KeyboardInterrupt gracefully
    process_all_cards(max_card_id=3)

    # Should have processed card 1 and saved progress
    assert mock_save_progress.call_count >= 1


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_process_all_cards_rate_limiting(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = "test_api_key"

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.text_to_embed = "test text"
    mock_card_business_class.return_value = mock_business

    process_all_cards(max_card_id=3)

    # Verify sleep was called for rate limiting
    assert mock_sleep.call_count == 3
    mock_sleep.assert_called_with(0.5)


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("os.path.exists")
@patch("os.remove")
@patch("time.sleep")
@patch("builtins.print")
def test_process_all_cards_progress_indicator(
    mock_print,
    mock_sleep,
    mock_remove,
    mock_exists,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    mock_getenv.return_value = "test_api_key"
    mock_exists.return_value = True

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.text_to_embed = "test text"
    mock_card_business_class.return_value = mock_business

    # Process cards including card 100 (divisible by 100)
    process_all_cards(max_card_id=101)

    # Check if progress indicator was printed (card 100)
    progress_prints = [
        call for call in mock_print.call_args_list if "Progress:" in str(call)
    ]
    assert len(progress_prints) >= 1


@patch("vectorize.get_last_processed_id")
@patch("vectorize.save_progress")
@patch("vectorize.CardDao")
@patch("vectorize.CardBusiness")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
@patch("time.sleep")
def test_process_all_cards_vectorize_called_with_correct_params(
    mock_sleep,
    mock_getenv,
    mock_load_dotenv,
    mock_card_business_class,
    mock_card_dao_class,
    mock_save_progress,
    mock_get_last_id,
):
    mock_get_last_id.return_value = 0
    api_key = "test_api_key_123"
    mock_getenv.return_value = api_key

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    mock_business = MagicMock()
    mock_business.text_to_embed = "test card description"
    mock_card_business_class.return_value = mock_business

    process_all_cards(max_card_id=1)

    # Verify vectorize was called with correct parameters
    expected_endpoint = "https://llm.lab.sspcloud.fr/ollama/api/embed"
    mock_business.vectorize.assert_called_once_with(
        "test card description", expected_endpoint, api_key
    )


@patch("vectorize.get_last_processed_id")
@patch("vectorize.CardDao")
@patch("vectorize.load_dotenv")
@patch("os.getenv")
def test_process_all_cards_all_already_processed(
    mock_getenv, mock_load_dotenv, mock_card_dao_class, mock_get_last_id
):
    # All cards already processed
    mock_get_last_id.return_value = 100
    mock_getenv.return_value = "test_api_key"

    mock_dao = MagicMock()
    mock_dao.__enter__.return_value = mock_dao
    mock_dao.__exit__.return_value = False
    mock_card_dao_class.return_value = mock_dao

    # max_card_id equals last processed
    process_all_cards(max_card_id=100)
