import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from .abstractDao import AbstractDao


class CardDao(AbstractDao):

    columns_valid = {
        "id",
        "card_key",
        "name",
        "ascii_name",
        "text",
        "type",
        "layout",
        "mana_cost",
        "mana_value",
        "converted_mana_cost",
        "face_converted_mana_cost",
        "face_mana_value",
        "face_name",
        "first_printing",
        "hand",
        "life",
        "loyalty",
        "power",
        "toughness",
        "side",
        "defense",
        "edhrec_rank",
        "edhrec_saltiness",
        "is_funny",
        "is_game_changer",
        "is_reserved",
        "has_alternative_deck_limit",
        "colors",
        "color_identity",
        "color_indicator",
        "types",
        "subtypes",
        "supertypes",
        "keywords",
        "subsets",
        "printings",
        "scryfall_oracle_id",
        "text_to_embed",
        "embedding",
        "raw",
    }

    def exist(self, id):
        """
        Check if a card with the given ID exists in the database.

        Args:
            id (int): The ID of the card to check. Must be a non-negative integer.

        Returns:
            bool: True if a card with the specified ID exists, False otherwise.

        Raises:
            TypeError: If `id` is not an integer.
            ValueError: If `id` is a negative integer.
            Exception: If there is an error connecting to the database.

        Notes:
            - The method connects to a PostgreSQL database using `psycopg2`.
            - It queries the `cards` table and checks for the presence of a row
              with the specified `id`.
            - Database connection is properly closed after execution.
        """
        if not isinstance(id, int):
            raise TypeError("Card ID must be an integer")
        if id < 0:
            raise ValueError("Card ID must be a positive integer")
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
            SELECT * FROM cards WHERE id = %s LIMIT 1;
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

    def get_by_id(self, id):
        """Fetch a card by its ID and return it as a dictionary.

        Args:
            card_id (int): The ID of the card to fetch.

        Returns:
            dict: A dictionary representing the card, where keys are column names.
                  Returns `None` if no card is found with the given ID.

        Raises:
            ValueError: If the provided `card_id` is not a positive integer.
            psycopg2.Error: If a database error occurs during the query execution.
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
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                sql_query = """
                SELECT * FROM cards WHERE id = %s LIMIT 1;
                """
                param = (id,)
                cursor.execute(sql_query, param)
                row = cursor.fetchone()
                return row
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close

    def create(self, **kwargs):
        """
        Insert a new record into the `cards` table.

        Parameters
        ----------
        **kwargs : dict
            Key-value pairs representing the columns and values to insert into the `cards` table.
            Only keys present in `self.columns_valid` (except 'id') are allowed.
            Missing columns will default to `None`.

        Returns
        -------
        dict
            A dictionary representing the newly created card, with all columns returned
            by the database, including auto-generated ones like `id`.

        Raises
        ------
        ValueError
            If `kwargs` contains any keys not listed in `self.columns_valid`.
        psycopg2.DatabaseError
            If an error occurs while connecting to the database or executing the query.

        Notes
        -----
        - The `id` column is assumed to be auto-generated
          by the database and should not be included in `kwargs`.
        - This function uses parameterized queries to prevent SQL injection.
        - Database credentials are currently hardcoded and
          should ideally be managed securely via environment variables.

        Example
        -------
        >>> card_manager = CardManager()
        >>> new_card = card_manager.create(name="Ace of Spades", value=14, suit="Spades")
        >>> print(new_card)
        {'id': 101, 'name': 'Ace of Spades', 'value': 14, 'suit': 'Spades'}
        """
        if not (set(kwargs.keys()).issubset(self.columns_valid)):
            raise ValueError(
                f"Invalid keys : {set(kwargs.keys()) - self.columns_valid}"
            )
        card_data = {
            key: kwargs.get(key, None) for key in self.columns_valid if key != "id"
        }
        # Add None for the keys None - specified.
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
            columns = ", ".join(card_data.keys())
            placeholders = ", ".join(["%s"] * len(card_data))
            sql_query = f"""
            INSERT INTO cards ({columns})
            VALUES ({placeholders})
            RETURNING *;
            """
            params = tuple(card_data.values())
            cursor.execute(sql_query, params)
            conn.commit()
            new_card = cursor.fetchone()
            return new_card
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close

    def update(self, id, *args, **kwargs):
        """
        Update a card in the database by its ID with the provided field values.

        This method checks that the card exists and that all provided field names
        are valid columns. It then constructs and executes an SQL UPDATE query
        using parameterized values to prevent SQL injection, commits the change,
        and returns the updated card as a dictionary.

        Parameters
        ----------
        id : int
            The unique identifier of the card to update. Must be a positive integer.
        *args
            Positional arguments are ignored; updates should be passed as keyword arguments.
        **kwargs
            Field names and their new values to update. Keys must be a subset of valid
            column names defined in `self.columns_valid`.

        Returns
        -------
        dict or None
            A dictionary representing the updated card if the update succeeds,
            or None if the card with the specified ID does not exist.

        Raises
        ------
        ValueError
            If any key in `kwargs` is not a valid column name.
        TypeError
            If `id` is not an integer or `kwargs` is not a dictionary.
        Exception
            If a database connection error occurs, the program exits after printing
            the error.
        """
        if self.exist(id):
            if not (set(kwargs.keys()).issubset(self.columns_valid)):
                raise ValueError(
                    f"Invalid keys : {set(kwargs.keys()) - self.columns_valid}"
                )
            columns = list(kwargs.keys())
            values = list(kwargs.values())
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
                set_clause = ", ".join([f"{col} = %s" for col in columns])
                sql_query = f"""
                    UPDATE cards
                    SET {set_clause}
                    WHERE id = %s
                    RETURNING *;
                """
                params = (*values, id)
                cursor.execute(sql_query, params)
                conn.commit()
                updated_card = cursor.fetchone()
                return updated_card
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close

    def delete(self, id):
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
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                sql_query = """
                DELETE FROM cards
                WHERE id = %s
                RETURNING *;
                """
                param = (id,)
                cursor.execute(sql_query, param)
                row = cursor.fetchone()
                return row
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close

    def edit_text_to_embed(self, embed_me, card_id):
        """Edit the text_to_embed value of a card.

        Args:
            embed_me (str): The new text to embed. Must be a non-empty string.
            card_id (int): The ID of the card to update. Must be a positive integer.

        Returns:
            int: The number of rows updated (should be 1 if successful).

        Raises:
            ValueError: If card_id is not a positive integer or if no card was
            found with the given ID.
            TypeError: If embed_me is not a string.
            psycopg2.Error: If a database error occurs during the query execution.
        """
        # Input validation
        if not isinstance(embed_me, str):
            raise TypeError("embed_me must be a string")

        if not embed_me.strip():
            raise ValueError("embed_me cannot be empty or whitespace only")

        if not isinstance(card_id, int) or card_id <= 0:
            raise ValueError("Card ID must be a positive integer")

        try:
            # Execute the update query
            query = sql.SQL("UPDATE cards SET text_to_embed = %s WHERE id = %s")
            self.cursor.execute(query, (embed_me, card_id))
            self.conn.commit()

            # Check if any rows were updated
            if self.cursor.rowcount == 0:
                raise ValueError(
                    f"No card found with ID {card_id}. No rows were updated."
                )

            return self.cursor.rowcount

        except psycopg2.Error as e:
            # Rollback in case of database error
            self.conn.rollback()
            # Add more specific error message
            raise psycopg2.Error(
                f"Database error while updating text_to_embed for card ID {card_id}: {str(e)}"
            )

    def faceted_search():
        """Allow multi-filter search across facets like type, set, color"""
        pass

    def filter_by_attributes():
        """Filter cards using structured fields (mana, color, type, etc.)"""
        pass

    def full_text_search():
        """Search cards by keywords in name, text, or type using text index"""
        pass

    def precomputed_tag_search():
        """Search using pre-labeled categories like removal, ramp, draw"""
        pass


if __name__ == "__main__":
    with CardDao() as dao:
        # print(dao.edit_text_to_embed("zaza",1))
        print(dao.get_card_by_id(420))
