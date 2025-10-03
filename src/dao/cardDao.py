import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from .abstractDao import AbstractDao


class CardDao(AbstractDao):
    VALID_COLUMNS = {
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
        if not isinstance(id, int):
            raise TypeError("Card ID must be an integer")
        if id < 0:
            raise ValueError("Id must be a positive integer")
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
