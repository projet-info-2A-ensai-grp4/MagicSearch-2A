import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from .abstractDao import AbstractDao


class UserDao(AbstractDao):
    def exist(self, id):
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
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            sql_query = """
            SELECT * FROM users WHERE id = %s LIMIT 1;
            """
            param = (id,)
            cursor.execute(sql_query, param)
            row = cursor.fetchone()
            return row is not None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close

    def getUsername(self, user_id):
        """
        Get the username by user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            username (str)

        Raises:
            ValueError: If the provided `user_id` is not a positive integer.
            psycopg2.Error: If a database error occurs during the query execution.
        """
        if self.exist(id):
            try:
                query = sql.SQL("SELECT username FROM users WHERE id = %s;")
                self.cursor.execute(query, (user_id,))
        
            except psycopg2.Error as e:
                # Log the error or handle it as needed
                raise psycopg2.Error(
                    f"Database error while fetching card with ID {user_id}: {e}"
                )

    def getEmail(self, user_id):
        """
        Get the email by user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            username (str)

        Raises:
            ValueError: If the provided `user_id` is not a positive integer.
            psycopg2.Error: If a database error occurs during the query execution.
        """
        if self.exist(id):
            try:
                query = sql.SQL("SELECT email FROM users WHERE id = %s;")
                self.cursor.execute(query, (user_id,))
            
            except psycopg2.Error as e:
                # Log the error or handle it as needed
                raise psycopg2.Error(
                    f"Database error while fetching card with ID {user_id}: {e}"
                )
                
    def signUp(self, username, email, password_hash):
        """
        Insert a new user into the database.
        
        Args:
            username (str): chosen username
            email (str): user email
            password_hash (str): hashed password (never store raw password!)
        
        Returns:
            int: the id of the newly created user
        """
        query = sql.SQL("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id;
        """)

        with self.conn.cursor() as cur:
            cur.execute(query, (username, email, password_hash))
            user_id = cur.fetchone()[0]
        
        self.conn.commit()
        return user_id

    def signIn():
        """
        Connect a user on its account.
        
        Args:
            username (str): chosen username
            password_hash (str): hashed password (never store raw password!)
        
        Returns:
            int: the id of the user
        """

    def create(self, *args, **kwargs):
        pass

    def get_by_id(self, id):
        pass

    def update(self, id, *args, **kwargs):
        pass

    def delete(self, entity_id):
        pass
