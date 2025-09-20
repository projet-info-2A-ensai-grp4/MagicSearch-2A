import psycopg2
from psycopg2 import sql


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
            return None
    
        except psycopg2.Error as e:
            # Log the error or handle it as needed
            raise psycopg2.Error(f"Database error while fetching card with ID {card_id}: {e}")
    

    def edit_text_to_embed(self, embed_me, card_id):
        """Edit the text_to_embed value of a card.

        Args:
            embed_me (str): The new text to embed.
            card_id (int): The ID of the card to update.

        Returns:
            int: The number of rows updated (should be 1 if successful).

        Raises:
            ValueError: If no card was found with the given ID.
        """
        query = sql.SQL("UPDATE cards SET text_to_embed = %s WHERE id = %s")
        self.cursor.execute(query, (embed_me, card_id))
        self.conn.commit()

        if self.cursor.rowcount == 0:
            raise ValueError(f"No card found with ID {card_id}. No rows were updated.")

        return self.cursor.rowcount

if __name__ == "__main__":
    with CardDao() as dao:
        # print(dao.edit_text_to_embed("zaza",1))
        print(dao.get_card_by_id(420))
