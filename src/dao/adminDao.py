import psycopg2
from .userDao import UserDao


class AdminDao(UserDao):
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
                    "SELECT user_id,              "
                    "       username,             "
                    "       email,                "
                    "       password_hash,        "
                    "       role_id               "
                    "FROM users                   "
                    "ORDER BY user_id             "
                )
                users_db = self.cursor.fetchall()
                return users_db
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
