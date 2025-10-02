import psycopg2
import warnings
from psycopg2 import sql
from .abstractDao import AbstractDao


class CardDao(AbstractDao):
    def get_card_by_id(self, card_id):
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
        if not isinstance(card_id, int) or card_id <= 0:
            raise ValueError("card_id must be a positive integer.")

        try:
            query = sql.SQL("SELECT * FROM cards WHERE id = %s;")
            self.cursor.execute(query, (card_id,))

            columns = [desc[0] for desc in self.cursor.description]
            row = self.cursor.fetchone()

            if row:
                return dict(zip(columns, row))
            else:
                warnings.warn(f"No card found with ID {card_id}. Returning None.", UserWarning)
                return None

        except psycopg2.Error as e:
            # Log the error or handle it as needed
            raise psycopg2.Error(
                f"Database error while fetching card with ID {card_id}: {e}"
            )

    def exist(self, id):
        pass

    def create(self, *args, **kwargs):
        pass

    def get_by_id(self, entity_id):
        pass

    def update(self, entity_id, *args, **kwargs):
        pass

    def delete(self, entity_id):
        pass

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
            raise ValueError("card_id must be a positive integer")

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
