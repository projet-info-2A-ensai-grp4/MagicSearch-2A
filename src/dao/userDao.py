import psycopg2
from .abstractDao import AbstractDao


class UserDao(AbstractDao):
    def exist(self, id):
        """
        Verify if an id is correct and exists in the database.

        Parameters
        ----------
        id : int
            The id we want to check.

        Returns
        -------
        bool
            True if 'id' exists in the database, False otherwise.

        Raises
        -------
        TypeError
            If the id is not an integer.
        ValueError
            If the id is not strictly positive.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        if not isinstance(id, int):
            raise TypeError("User id must be an integer")
        if id <= 0:
            raise ValueError("The user id must be positive")
        try:
            with self:
                self.cursor.execute(
                    "SELECT id         "
                    "FROM users        "
                    "WHERE id = %s     "
                    "LIMIT 1           ",
                    (id,),
                )
                user = self.cursor.fetchone()
            return user is not None
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # CREATE

    def create(self, username, email, password_hash):
        """
        Create a user in the users database.

        Parameters
        ----------
        username : str
            The username.
        email: str
            The user's email.
        password_hash: str
            The securely hashed password of the user.

        Returns:
        --------
        new_user: dict
            Dictionary containing the newly created user's information, such as
            'id', 'username', 'email', 'password_hash' and 'role'.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "INSERT INTO users (username,        "
                    "                   email,           "
                    "                   password_hash)   "
                    "VALUES (%s, %s, %s)                 "
                    "RETURNING id,                       "
                    "          username,                 "
                    "          email,                    "
                    "          password_hash             ",
                    (username, email, password_hash),
                )
                new_user = self.cursor.fetchone()
                self.conn.commit()
                new_user["role"] = "player"
                return new_user
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # READ
    def get_all(self):
        """
        Get every users in the database.

        Returns:
        --------
        users_db: list
            The list of dictionaries containing the users's information, such
            as 'id', 'username', 'email', 'password_hash' and 'role.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT id,              "
                    "       username,        "
                    "       email,           "
                    "       password_hash,   "
                    "       role             "
                    "FROM users              "
                    "ORDER BY id             "
                )
                users_db = self.cursor.fetchall()
                return users_db
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    def get_by_id(self, id):
        """
        Get a user in the database with its id.

        Parameters
        ----------
        id : int
            The user's id.

        Returns:
        --------
        user : dict or None
            - Dictionary containing the newly created user's information, such
              as 'id', 'username', 'email', 'password_hash' and 'role, if the
              user exists.
            - None if no user with the given id exists in the database.

        Raises:
        -------
        TypeError
            If the id is not an integer.
        ValueError
            If the id is not strictly positive.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        if self.exist(id):
            try:
                with self:
                    self.cursor.execute(
                        "SELECT id,             "
                        "       username,       "
                        "       email,          "
                        "       password_hash,  "
                        "       role            "
                        "FROM users             "
                        "WHERE id = %s          ",
                        (id,),
                    )
                    user = self.cursor.fetchone()
                return user
            except psycopg2.OperationalError as e:
                raise ConnectionError(
                    f"Database connection failed: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Unexpected database error: {e}") from e

    def get_by_username(self, username):
        """
        Get a user in the database with its username.

        Parameters
        ----------
        username : str
            The username.

        Returns:
        --------
        user : dict or None
            - Dictionary containing the newly created user's information, such
              as 'id', 'username', 'email', 'password_hash' and 'role', if the
              user exists.
            - None if no user with the given id exists in the database.

        Raises:
        -------
        TypeError
            If the id is not an integer.
        ValueError
            If the id is not strictly positive.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT id,             "
                    "       username,       "
                    "       email,          "
                    "       password_hash,  "
                    "       role            "
                    "FROM users             "
                    "WHERE username = %s    ",
                    (username,),
                )
                user = self.cursor.fetchone()
            return user
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    def new_email(self, email):
        """
        Check if an email is already used.

        Parameters
        ----------
        email :
            The email used to sign up.

        Returns:
        --------
        bool :
            True if the email is not already in the database.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT id             "
                    "FROM users            "
                    "WHERE email = %s      ",
                    (email),
                )
                users_db = self.cursor.fetchone()
                if users_db is None:
                    return True
                return False
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # UPDATE
    def update(self, id, username=None, email=None, password_hash=None):
        """
        Update a user's information.

        Parameters
        ----------
        id : int
            The user's id.
        username : str, optional
            The updated username. Default is None.
        email : str, optional
            The updated user's email. Default is None.
        password_hash : str, optional
            The updated securely hashed password of the user. Default is None.

        Returns:
        --------
        user : dict
            Dictionary containing the updated user's information, such as 'id',
            'username', 'email', 'password_hash' and 'role.

        Raises:
        -------
        TypeError
            If the id is not an integer.
        ValueError
            If the id is not strictly positive.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        if self.exist(id):
            updates = []
            params = []
            if username is not None:
                updates.append("username = %s")
                params.append(username)
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            if password_hash is not None:
                updates.append("password_hash = %s")
                params.append(password_hash)
            if not updates:
                raise ValueError(
                    "At least one field to update must be provided"
                )
            params.append(id)
            query = (
                "UPDATE users               "
                f"SET {', '.join(updates)}  "
                "WHERE id = %s              "
                "RETURNING id,              "
                "          username,        "
                "          email,           "
                "          password_hash,   "
                "          role             "
            )

            try:
                with self:
                    self.cursor.execute(query, params)
                    updated_user = self.cursor.fetchone()
                    self.conn.commit()
                    return updated_user
            except psycopg2.OperationalError as e:
                raise ConnectionError(
                    f"Database connection failed: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Unexpected database error: {e}") from e

    # DELETE
    def delete(self, id):
        """
        Delete a user from the users database.

        Parameters
        ----------
        id : int
            The user's id.

        Returns:
        --------
        user : dict
            Dictionary containing the deleted user's information, such as 'id',
            'username', 'email', 'password_hash' and 'role'.

        Raises:
        -------
        TypeError
            If the id is not an integer.
        ValueError
            If the id is not strictly positive.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        if self.exist(id):
            conn = None
            try:
                with self:
                    self.cursor.execute(
                        "DELETE FROM users         "
                        "WHERE id = %s             "
                        "RETURNING id,             "
                        "          username,       "
                        "          email,          "
                        "          password_hash,  "
                        "          role            ",
                        (id,),
                    )
                    del_user = self.cursor.fetchone()
                    self.conn.commit()
                    return del_user
            except psycopg2.OperationalError as e:
                raise ConnectionError(
                    f"Database connection failed: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Unexpected database error: {e}") from e
            finally:
                if conn:
                    conn.close()
