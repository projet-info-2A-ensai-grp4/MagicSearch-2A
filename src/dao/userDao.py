import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from .abstractDao import AbstractDao


class UserDao(AbstractDao):
    def exist(self, id):
        """
        Verifies if a user exists with its ID.
        """
        if not isinstance(id, int):
            raise TypeError("User ID must be an integer")
        if id < 0:
            raise ValueError("ID must be a positive integer")
        try:
            conn = psycopg2.connect(
                dbname="defaultdb",
                user="user-victorjean",
                password="pr9yh1516s57jjnmw7ll",
                host="postgresql-885217.user-victorjean",
                port="5432",
            )
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT *        "
                "FROM users      "
                "WHERE id = %s   "
                "LIMIT 1         ",
                (id,)
            )
            row = cursor.fetchone()
        cursor.close()
        return row is not None

    # CREATE

    def create(self, username, email, password_hash):
        """
        Create a new user into the users database.

        Args:
        user

        Returns:
        id (int): the ID of the newly created user.
        """
        try:
            conn = psycopg2.connect(
                dbname="defaultdb",
                user="user-victorjean",
                password="pr9yh1516s57jjnmw7ll",
                host="postgresql-885217.user-victorjean",
                port="5432",
            )
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, email, password_hash)   "
                "VALUES (%s, %s, %s)  "
                "   RETURNING id_user                                 ",
                (username, email, password_hash),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id

    # READ

    def get_all(self):
        """
        Get all users of the database.
        """
        try:
            conn = psycopg2.connect(
                dbname="defaultdb",
                user="user-victorjean",
                password="pr9yh1516s57jjnmw7ll",
                host="postgresql-885217.user-victorjean",
                port="5432",
            )
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id,            "
                "       username,      "
                "       email,         "
                "       password_hash  "
                "FROM users            "
            )
            users_db = cur.fetchall()
            return users_db

    def get_by_id(self, id):
        """
        Get infos about the user from its ID.

        Args:
        id (int): the user ID

        Returns:
        user (dict): {"username", "email", "password_hash"}
        """
        if self.exist(id):
            try:
                conn = psycopg2.connect(
                    dbname="defaultdb",
                    user="user-victorjean",
                    password="pr9yh1516s57jjnmw7ll",
                    host="postgresql-885217.user-victorjean",
                    port="5432",
                )
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                exit()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id,              "
                    "       username,        "
                    "       email,           "
                    "       password_hash,   "
                    "FROM users              "
                    "WHERE id = %s           ",
                    (id,)
                )
                user = cursor.fetchone()
            conn.close()
            return user

    def update(self, id, username=None, email=None, password_hash=None):
        """
        Update the users database.

        Args:

        Returns:
            user (dict): the updated user
        """
        if self.exist(id):
            updates = []
            params = []
            if username is not None:
                updates.append(sql.SQL("username = %s"))
                params.append(username)
            if email is not None:
                updates.append(sql.SQL("email = %s"))
                params.append(email)
            if password_hash is not None:
                updates.append(sql.SQL("password_hash = %s"))
                params.append(password_hash)
            if not updates:
                raise ValueError("At least one field to update must be provided")
            params.append(id)
            query = sql.SQL("""
                UPDATE users
                SET {set_clause}
                WHERE user_id = %s
                RETURNING user_id,
                          username,
                          email,
                          password_hash
            """).format(set_clause=sql.SQL(", ").join(updates))

            conn = None
            try:
                conn = psycopg2.connect(
                    dbname="defaultdb",
                    user="user-victorjean",
                    password="pr9yh1516s57jjnmw7ll",
                    host="postgresql-885217.user-victorjean",
                    port="5432",
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    row = cur.fetchone()
                    conn.commit()
                    return row
            finally:
                if conn:
                    conn.close()

    def delete(self, entity_id):
        pass
