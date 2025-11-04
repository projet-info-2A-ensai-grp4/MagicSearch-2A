# export PYTHONPATH=~/work/MagicSearch-2A/src
# export DB_HOST=postgresql-885217.user-victorjean
# export DB_PORT=5432
# export DB_NAME=defaultdb
# export DB_USER=user-victorjean
# export DB_PASSWORD=pr9yh1516s57jjnmw7ll

import psycopg2
from psycopg2 import sql
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

    def shape(self):
        """
        Retrieve the shape of the cards dataset in the database.

        This method connects to the PostgreSQL database and fetches two key pieces
        of information about the "cards" table:

        1. The total number of rows (cards) in the table.
        2. The total number of valid columns as defined in the DAO.

        Returns
        -------
        tuple
            A tuple of the form `(row_count, column_count)` where:
            - `row_count` (int): The number of rows in the `cards` table.
            - `column_count` (int): The number of columns tracked in `self.columns_valid`.

        Raises
        ------
        Exception
            If a database connection cannot be established, the method prints the
            error and exits the program.
        """
        try:
            with self:
                sql_query = """
                SELECT count(*) FROM cards;
                """
                self.cursor.execute(sql_query)
                row = self.cursor.fetchone()
                return row.get("count"), len(self.columns_valid)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise

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
            with self:
                sql_query = """
                SELECT * FROM cards WHERE id = %s LIMIT 1;
                """
                param = (id,)
                self.cursor.execute(sql_query, param)
                row = self.cursor.fetchone()
                return row is not None

        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

    def get_by_id(self, id):
        """Fetch a card by its ID and return it as a dictionary.

        Args:
            card_id (int): The ID of the card to fetch.

        Returns:
            dict: A dictionary representing the card, where keys are column
            names.
                  Returns `None` if no card is found with the given ID.

        Raises:
            ValueError: If the provided `card_id` is not a positive integer.
            psycopg2.Error: If a database error occurs during the query
            execution.
        """
        if self.exist(id):
            try:
                with self:
                    sql_query = """
                    SELECT * FROM cards WHERE id = %s LIMIT 1;
                    """
                    param = (id,)
                    self.cursor.execute(sql_query, param)
                    row = self.cursor.fetchone()
                    return row
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                exit()

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
            with self:
                columns = ", ".join(card_data.keys())
                placeholders = ", ".join(["%s"] * len(card_data))
                sql_query = f"""
                    INSERT INTO cards ({columns})
                    VALUES ({placeholders})
                    RETURNING *;
                    """
                params = tuple(card_data.values())
                self.cursor.execute(sql_query, params)
                self.conn.commit()
                new_card = self.cursor.fetchone()
                return new_card
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

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
                with self:
                    set_clause = ", ".join([f"{col} = %s" for col in columns])
                    sql_query = f"""
                        UPDATE cards
                        SET {set_clause}
                        WHERE id = %s
                        RETURNING *;
                    """
                    params = (*values, id)
                    self.cursor.execute(sql_query, params)
                    self.conn.commit()
                    updated_card = self.cursor.fetchone()
                    return updated_card
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                exit()

    def delete(self, id):
        """
        Delete a card from the database by its ID.

        This method checks if a card with the given ID exists using `self.exist(id)`.
        If it exists, it deletes the card from the `cards` table and returns the deleted row.
        Uses a context manager (`dbConnection`) to safely handle the database connection
        and cursor. Commits the transaction after deletion.

        Parameters:
            id (int): The ID of the card to delete. Must be a positive integer.

        Returns:
            dict: The deleted row as a dictionary if the deletion was successful.
            None: If the card does not exist.

        Raises:
            TypeError: If `id` is not an integer.
            ValueError: If `id` is a negative integer.
            Exception: If there is an error connecting to the database or executing the query.

        Example:
            deleted_card = obj.delete(42)
            if deleted_card:
                print("Card deleted:", deleted_card)
            else:
                print("Card not found.")
        """
        if self.exist(id):
            try:
                with self:
                    sql_query = """
                    DELETE FROM cards
                    WHERE id = %s
                    RETURNING *;
                    """
                    param = (id,)
                    self.cursor.execute(sql_query, param)
                    row = self.cursor.fetchone()
                    self.conn.commit()
                    return row
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                exit()

    def edit_text_to_embed(self, embed_me, card_id):
        """Edit the text_to_embed value of a card.

        Args:
            embed_me (str): The new text to embed. Must be a non-empty string.
            card_id (int): The ID of the card to update. Must be a positive
            integer.

        Returns:
            int: The number of rows updated (should be 1 if successful).

        Raises:
            ValueError: If card_id is not a positive integer or if no card was
            found with the given ID. TypeError: If embed_me is not a string.
            psycopg2.Error: If a database error occurs during the query
            execution.
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
                f"Database error while updating text_to_embed for card ID "
                f"{card_id}: {str(e)}"
            )

    def edit_vector(self, vector_me: list, card_id: int) -> int:
        """Edit the embedding vector of a card.

        Args:
            vector_me (list): The new embedding vector. Must be a non-empty
            list of numbers. card_id (int): The ID of the card to update. Must
            be a positive integer.

        Returns:
            int: The number of rows updated (should be 1 if successful).

        Raises:
            ValueError: If card_id is not a positive integer or if no card was
            found with the given ID. TypeError: If vector_me is not a list or
            contains non-numeric values. psycopg2.Error: If a database error
            occurs during the query execution.
        """
        # Input validation
        if not isinstance(vector_me, list):
            raise TypeError("vector_me must be a list")
        if not vector_me:
            raise ValueError("vector_me cannot be empty")
        if not all(isinstance(x, (int, float)) for x in vector_me):
            raise TypeError("vector_me must contain only numeric values")
        if not isinstance(card_id, int) or card_id <= 0:
            raise ValueError("card_id must be a positive integer")

        try:
            # Execute the update query
            query = sql.SQL("UPDATE cards SET embedding = %s WHERE id = %s")
            self.cursor.execute(query, (vector_me, card_id))
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
                f"Database error while updating embedding for card ID "
                f"{card_id}: {str(e)}"
            )

    def filter(
        self,
        order_by: str,
        asc: bool = True,
        limit: int = 100,
        offset: int = 0,
        **kwargs,
    ):
        """
        Retrieves cards from the database using dynamic filters.

        This method builds a SQL SELECT query on the `cards` table with:
        - Dynamic filters passed via **kwargs
        - Optional sorting (ORDER BY)
        - Pagination (LIMIT / OFFSET)

        Parameters:
        -----------
        order_by : str, optional
            The column name to sort the results by. Must be in `self.columns_valid`.
        asc : bool, optional, default=True
            Sorting direction: True for ascending (ASC), False for descending (DESC).
        limit : int, optional, default=100
            Maximum number of results to return.
        offset : int, optional, default=0
            Offset for pagination.
        **kwargs : dict
            Dynamic column filters, where each key is a column name and the value is the filter:
            - Single value → filters as `col = value`
            - List or tuple → filters as `col IN (value1, value2, ...)`
            - None → filter evaluates as FALSE (returns no results)

        Behavior:
        ---------
        1. Validates that all filter keys are in `self.columns_valid`.
        2. Validates that `order_by` is valid if provided.
        3. Builds the WHERE clause dynamically:
        - `col = %s` for scalar values
        - `col IN (%s, %s, ...)` for lists/tuples
        - `FALSE` for None values
        4. Adds ORDER BY if requested.
        5. Adds LIMIT and OFFSET for pagination.
        6. Executes the query using placeholders `%s` to prevent SQL injection.
        7. Returns results as a list of dictionaries (RealDictCursor).

        Returns:
        --------
        list[dict]
            List of dictionaries representing the cards retrieved from the `cards` table.
        """
        if not (set(kwargs.keys()).issubset(self.columns_valid)):
            raise ValueError(
                f"Invalid keys : {set(kwargs.keys()) - self.columns_valid}"
            )
        if order_by not in self.columns_valid:
            raise ValueError(f"Invalid order_by: {order_by}")
        try:
            with self:
                base_query = "SELECT * FROM cards WHERE TRUE"
                params = []
                filters = []
                for col, vals in kwargs.items():
                    if vals is not None:
                        if isinstance(vals, (list, tuple)):
                            placeholders = ",".join(["%s"] * len(vals))
                            filters.append(f"{col} IN ({placeholders})")
                            params.extend(vals)
                        else:
                            filters.append(f"{col} = %s")
                            params.append(vals)
                    else:
                        filters.append("FALSE")
                if filters:
                    base_query += " AND " + " AND ".join(filters)
                if order_by:
                    direction = "ASC" if asc else "DESC"
                    base_query += f" ORDER BY {order_by} {direction}"
                base_query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                self.cursor.execute(base_query, params)
                return self.cursor.fetchall()
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

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
        print(dao.get_card_by_id(420))
