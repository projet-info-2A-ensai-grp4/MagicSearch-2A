from dao.abstractDao import AbstractDao
from dao.cardDao import CardDao
import psycopg2


class DeckDao(AbstractDao):
    # CREATE

    def create(self, user_id, name, deck_type):
        """
        Create a new deck for a user.

        Parameters
        ----------
        user_id : int
            The user id.
        name : str
            The name of the deck.
        deck_type : str
            The type of the deck.

        Returns
        -------
        row : dict
            Dictionary containing the deck_id and deck informations.

        Raises
        ------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "INSERT INTO decks (name, type) "
                    "VALUES (%s, %s)             "
                    "RETURNING deck_id, name, type",
                    (name, deck_type),
                )
                row = self.cursor.fetchone()

                self.cursor.execute(
                    "INSERT INTO user_deck_link (user_id, deck_id) "
                    "VALUES (%s, %s)                               ",
                    (user_id, row['deck_id']),
                )

                self.conn.commit()
                return row
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # READ

    def exist(self, id):
        """
        Checks if a deck with the given ID exists.

        Parameters
        ----------
        id : int
            ID of the deck to check.

        Returns
        -------
        bool :
            True if the deck exists, False otherwise.

        Raises
        ------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT deck_id FROM decks "
                    "WHERE deck_id = %s        "
                    "LIMIT 1                   ",
                    (id,),
                )
                return self.cursor.fetchone() is not None
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    def get_by_id(self, id):
        """
        Retrieves all information of a deck by its ID, including its cards.

        Parameters
        ----------
        id : int
            ID of the deck

        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT c.id, c.name, c.image_url, dc.quantity, d.name, d.type "
                    "FROM decks d                                                    "
                    "JOIN deck_cards dc ON d.deck_id = dc.deck_id                    "
                    "JOIN cards c ON dc.card_id = c.id                               "
                    "WHERE d.deck_id = %s;                                           ",
                    (id,),
                )
                results = self.cursor.fetchall()
                return results
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    def get_all_decks_from_user(self, user_id: int):
        """
        Retrieves all the decks of a specific user.

        Parameters
        ----------
        user_id : int
            User ID to fetch decks for.

        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT d.deck_id, d.name, d.type "
                    "FROM decks d                       "
                    "JOIN user_deck_link ud             "
                    "ON d.deck_id = ud.deck_id          "
                    "WHERE ud.user_id = %s              ",
                    (user_id,),
                )
                results = self.cursor.fetchall()
                return results

        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # UPDATE

    def update(self, id):
        """
        The update method is not useful for the DeckDao class.
        """
        pass

    def add_card_to_deck(self, card_id, deck_id):
        """
        Adds a card to a deck. If the card already exists in the deck, its quantity
        is increased by 1.

        Parameters
        ----------
        card_id : int
            The card id to add.
        deck_id : int
            The deck id to which the card will be added.
        """
        card = CardDao()
        if not card.exist(card_id):
            raise ValueError(f"Card {card_id} does not exist.")
        if not self.exist(deck_id):
            raise ValueError(f"Deck {deck_id} does not exist.")

        try:
            with self:
                self.cursor.execute(
                    "INSERT INTO deck_cards(deck_id, card_id, quantity) "
                    "VALUES (%s, %s, 1)                                 "
                    "ON CONFLICT (deck_id, card_id)                     "
                    "DO UPDATE SET quantity = deck_cards.quantity + 1;  ",
                    (deck_id, card_id),
                )
                rows = self.cursor.fetchall()
                return rows
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    def remove_card_from_deck(self, card_id, deck_id):
        """
        Removes a card from a deck.

        Parameters
        ----------
        card_id : int
            The card id to remove.
        deck_id : int
            The deck id from which the card will be removed.
        """
        card = CardDao()
        if not card.exist(card_id):
            raise ValueError(f"Card {card_id} does not exist.")
        if not self.exist(deck_id):
            raise ValueError(f"Deck {deck_id} does not exist.")

        try:
            with self:
                self.cursor.execute(
                    "DELETE FROM deck_cards                 "
                    "WHERE deck_id = %s AND card_id = %s    "
                    "RETURNING *                            ",
                    (deck_id, card_id),
                )
                deleted_row = self.cursor.fetchone()
                self.conn.commit()
                return deleted_row
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # DELETE

    def delete(self, id):
        """
        Delete a deck by its ID, including all associated cards and user links.
        """
        try:
            with self:
                # Supprimer les cartes du deck
                self.cursor.execute(
                    "DELETE FROM deck_cards "
                    "WHERE deck_id = %s     ",
                    (id,),
                )

                # Supprimer le lien user-deck
                self.cursor.execute(
                    "DELETE FROM user_deck_link "
                    "WHERE deck_id = %s         ",
                    (id,),
                )

                # Supprimer le deck et récupérer les infos supprimées
                self.cursor.execute(
                    "DELETE FROM decks              "
                    "WHERE deck_id = %s             "
                    "RETURNING deck_id, name, type  ",
                    (id,),
                )

                deleted_deck = self.cursor.fetchone()
                self.conn.commit()
                return deleted_deck
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
