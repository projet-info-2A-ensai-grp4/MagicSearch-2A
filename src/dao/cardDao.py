import psycopg2
import warnings
from psycopg2 import sql
import json


class CardDao:
    def __init__(self):
        self.conn_params = {
            "host": "postgresql-885217.user-victorjean",
            "port": 5432,
            "database": "defaultdb",
            "user": "user-victorjean",
            "password": "pr9yh1516s57jjnmw7ll",
        }
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Enable context manager support."""
        self.conn = psycopg2.connect(**self.conn_params)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are closed."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_card_by_id(self, card_id):
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
        if not isinstance(card_id, int) or card_id <= 0:
            raise ValueError("card_id must be a positive integer.")

        try:
            query = sql.SQL("SELECT * FROM cards WHERE id = %s;")
            self.cursor.execute(query, (card_id,))

            columns = [desc[0] for desc in self.cursor.description]
            row = self.cursor.fetchone()

            if row:
                card_data = dict(zip(columns, row))

                # embedding is a list
                if card_data["embedding"] is not None:
                    card_data["embedding"] = json.loads(card_data["embedding"])
                return card_data

            else:
                warnings.warn(
                    f"No card found with ID {card_id}. Returning None.",
                    UserWarning,
                )
                return None

        except psycopg2.Error as e:
            # Log the error or handle it as needed
            raise psycopg2.Error(
                f"Database error while fetching card with ID {card_id}: {e}"
            )

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
            raise ValueError("card_id must be a positive integer")

        try:
            # Execute the update query
            query = sql.SQL(
                "UPDATE cards SET text_to_embed = %s WHERE id = %s"
            )
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


if __name__ == "__main__":
    with CardDao() as dao:
        print(dao.get_card_by_id(420))
