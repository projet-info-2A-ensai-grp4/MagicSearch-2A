from dao.userDao import UserDao


class UserService:
    def __init__(self, username, email, password_hash, user_dao):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.user = user_dao

    def valid_username(self):
        """
        Validate a username based on specific rules:
            - The username cannot be empty
            - The username must have between 3 and 20 characters
            - The username must have only letters, numbers, '-', '_', '.'

        Parameters
        ----------
        username : str
            The username to validate.

        Returns
        -------
        bool
            True if 'id' exists in the database, False otherwise.

        Raises
        ------
        ValueError
            If the username is empty, has less than 3 or more than 20
            characters, does not start with a letter or uses unauthorized
            characters.
        """
        if self.username is None:
            raise ValueError("The username cannot be empty")
        username = self.username.strip()
        if not (3 <= len(username) <= 20):
            raise ValueError("The username must have between 3 and 20 characters")
        allowed_symbols = {"-", "_", "."}
        for char in username:
            if not (char.isalnum() or char in allowed_symbols):
                raise ValueError(
                    f"Unauthorized character: '{char}' (only letters, numbers "
                    f"and '-', '_', '.')"
                )
        if not username[0].isalpha():
            raise ValueError("The username has to begin with a letter")
        return True

    def signUp(self):
        """
        Create a user account.

        Parameters
        ----------
        username : str
            The username.
        hash_password : str
            The hashed password.

        Returns
        -------
        new_user : dict
            Dictionary containing the newly created user's information, such as
            'id', 'username', 'email' and 'password_hash'.
        """
        if not self.valid_username():
            raise ValueError("This username is not valid")
        if self.actual_user.get_by_username(self.username) is not None:
            raise ValueError("This username is already used")
        if not self.actual_user.new_email(self.email):
            raise ValueError("This email is already used")
        new_user = self.actual_user.create(
            self.username, self.email, self.password_hash
        )
        return new_user

    def signIn(self):
        """
        Log in to an account.

        Parameters
        ----------
        username : str
            The username.
        password_hash : str
            The hashed password.

        Returns
        -------
        user : dict
            Dictionary containing the user's information, such as 'id',
            'username', 'email' and 'password_hash'.

        Raises
        ------
        ValueError :
            If the username does not exist in the database.
        """
        user = self.actual_user.get_by_username(self.username)
        if user is None:
            raise ValueError("This username does not exist")
        if user["password_hash"] != self.password_hash:
            raise ValueError("Invalid password")
        return user
