import psycopg2
from psycopg2.extras import RealDictCursor
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
        conn = None
        try:
            conn = psycopg2.connect(
                dbname="defaultdb",
                user="user-victorjean",
                password="pr9yh1516s57jjnmw7ll",
                host="postgresql-885217.user-victorjean",
                port="5432",
            )
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT *          "
                    "FROM users        "
                    "WHERE id = %s     "
                    "LIMIT 1           ",
                    (id,),
                )
                user = cursor.fetchone()
            return user is not None
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
        finally:
            if conn:
                conn.close()

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
            'id', 'username', 'email' and 'password_hash'.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        conn = None
        try:
            conn = psycopg2.connect(
                dbname="defaultdb",
                user="user-victorjean",
                password="pr9yh1516s57jjnmw7ll",
                host="postgresql-885217.user-victorjean",
                port="5432",
            )
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
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
                new_user = cursor.fetchone()
                conn.commit()
                return new_user
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
            raise ValueError(
                f"User with email '{email}' already exists."
            ) from e
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
        finally:
            if conn:
                conn.close()

    # READ
    def get_all(self):
        """
        Get every users in the database.

        Returns:
        --------
        users_db: list
            The list of dictionaries containing the users's information, such
            as 'id', 'username', 'email' and 'password_hash'.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        conn = None
        try:
            conn = psycopg2.connect(
                dbname="defaultdb",
                user="user-victorjean",
                password="pr9yh1516s57jjnmw7ll",
                host="postgresql-885217.user-victorjean",
                port="5432",
            )
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id,              "
                    "       username,        "
                    "       email,           "
                    "       password_hash    "
                    "FROM users              "
                    "ORDER BY id             "
                )
                users_db = cursor.fetchall()
                return users_db
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
        finally:
            if conn:
                conn.close()

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
              as 'id', 'username', 'email' and 'password_hash', if the user
              exists.
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
            conn = None
            try:
                conn = psycopg2.connect(
                    dbname="defaultdb",
                    user="user-victorjean",
                    password="pr9yh1516s57jjnmw7ll",
                    host="postgresql-885217.user-victorjean",
                    port="5432",
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT id,             "
                        "       username,       "
                        "       email,          "
                        "       password_hash   "
                        "FROM users             "
                        "WHERE id = %s          ",
                        (id,),
                    )
                    user = cursor.fetchone()
                return user
            except psycopg2.OperationalError as e:
                raise ConnectionError(
                    f"Database connection failed: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Unexpected database error: {e}") from e
            finally:
                if conn:
                    conn.close()

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
            'username', 'email' and 'password_hash'.

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
                f"SET {', '.join(updates)}   "
                "WHERE id = %s              "
                "RETURNING id,              "
                "          username,        "
                "          email,           "
                "          password_hash    "
            )

            conn = None
            try:
                conn = psycopg2.connect(
                    dbname="defaultdb",
                    user="user-victorjean",
                    password="pr9yh1516s57jjnmw7ll",
                    host="postgresql-885217.user-victorjean",
                    port="5432",
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    updated_user = cursor.fetchone()
                    conn.commit()
                    return updated_user
            except psycopg2.OperationalError as e:
                raise ConnectionError(
                    f"Database connection failed: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Unexpected database error: {e}") from e
            finally:
                if conn:
                    conn.close()

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
            'username', 'email' and 'password_hash'.

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
                conn = psycopg2.connect(
                    dbname="defaultdb",
                    user="user-victorjean",
                    password="pr9yh1516s57jjnmw7ll",
                    host="postgresql-885217.user-victorjean",
                    port="5432",
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "DELETE FROM users         "
                        "WHERE id = %s             "
                        "RETURNING id,             "
                        "          username,       "
                        "          email,          "
                        "          password_hash   ",
                        (id,),
                    )
                    del_user = cursor.fetchone()
                    conn.commit()
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
