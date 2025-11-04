import pytest

from services.userService import UserService


# Tests valid_username()
def test_valid_username_ok():
    user1 = UserService("bruce", "brucewayne@gotham.com", "abc")
    user2 = UserService("bruce_wayne", "brucewayne@gotham.com", "abc")
    user3 = UserService("bruce25", "brucewayne@gotham.com", "abc")
    assert user1.valid_username() is True
    assert user2.valid_username() is True
    assert user3.valid_username() is True


def test_valid_username_empty():
    user = UserService(None, "brucewayne@gotham.com", "abc")
    with pytest.raises(ValueError, match="The username cannot be empty"):
        user.valid_username()


def test_valid_username_length():
    user1 = UserService("br", "brucewayne@gotham.com", "abc")
    user2 = UserService(
        "bruce_wayne_batman_gotham_city", "brucewayne@gotham.com", "abc"
    )
    with pytest.raises(
        ValueError, match="The username must have between 3 and 20 characters"
    ):
        user1.valid_username()
    with pytest.raises(
        ValueError, match="The username must have between 3 and 20 characters"
    ):
        user2.valid_username()


def test_valid_username_symbol():
    user1 = UserService("bruce$", "brucewayne@gotham.com", "abc")
    user2 = UserService("bruce#", "brucewayne@gotham.com", "abc")
    with pytest.raises(
        ValueError,
        match=r"Unauthorized character: '\$' \(only letters, numbers"
        r" and '-', '_', '\.'\)",
    ):
        user1.valid_username()
    with pytest.raises(
        ValueError,
        match=r"Unauthorized character: '\#' \(only letters, numbers"
        r" and '-', '_', '\.'\)",
    ):
        user2.valid_username()


def test_valid_username_begin():
    user1 = UserService("25bruce", "brucewayne@gotham.com", "abc")
    user2 = UserService("-bruce", "brucewayne@gotham.com", "abc")
    with pytest.raises(
        ValueError, match="The username has to begin with a letter"
    ):
        user1.valid_username()
    with pytest.raises(
        ValueError, match="The username has to begin with a letter"
    ):
        user2.valid_username()


# Tests signUp()
