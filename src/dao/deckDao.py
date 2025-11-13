from dao.abstractDao import AbstractDao
from dao.cardDao import CardDao
from dao.playerDao import PlayerDao


class DeckDao(AbstractDao):
    columns_valid = {"deck_id", "name", "type"}

    def shape(self):
        """
        Returns the shape of the decks table as a tuple.
        Returns:
            tuple: (number of rows in the decks table, number of valid columns)
        """
        try:
            with self:
                sql_query = """
                SELECT count(deck_id) FROM decks;
                """
                self.cursor.execute(sql_query)
                row = self.cursor.fetchone()
                return row.get("count"), len(self.columns_valid)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise

    def exist(self, id):
        """
        Checks if a deck with the given ID exists.

        Args:
            id (int): Deck ID to check.

        Returns:
            bool: True if the deck exists, False otherwise.

        Raises:
            TypeError: If id is not an integer.
            ValueError: If id is negative.
        """
        if not isinstance(id, int):
            raise TypeError("Deck ID must be an integer")
        if id < 0:
            raise ValueError("Deck ID must be a positive integer")
        try:
            with self:
                sql_query = """
                SELECT deck_id FROM decks WHERE deck_id = %s LIMIT 1;
                """
                param = (id,)
                self.cursor.execute(sql_query, param)
                row = self.cursor.fetchone()
                return row is not None

        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

    def get_by_id(self, id):
        """
        Retrieves all information of a deck by its ID, including its cards.

        Args:
            id (int): Deck ID to fetch.

        Returns:
            list[dict]: List of card information in the deck.
        """
        if self.exist(id):
            try:
                with self:
                    sql_query = """
                    SELECT D.name, C.*
                    FROM decks D
                    JOIN deck_cards DC
                    ON D.deck_id = DC.deck_id
                    JOIN cards C ON C.id = DC.card_id
                    WHERE D.deck_id = %s;
                    """
                    param = (id,)
                    self.cursor.execute(sql_query, param)
                    row = self.cursor.fetchall()
                    return row
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                exit()

    def create(self, **kwargs):
        """
        Creates a new deck with the provided attributes.

        Args:
            **kwargs: Keyword arguments corresponding to valid deck columns
                      (excluding deck_id if auto-generated).

        Returns:
            dict: The newly created deck record.

        Raises:
            ValueError: If invalid keys are provided or no data is given.
        """
        try:
            invalid_keys = set(kwargs.keys()) - self.columns_valid
            if invalid_keys:
                raise ValueError(f"Invalid keys: {invalid_keys}")

            insert_data = {k: v for k, v in kwargs.items() if k != "deck_id"}

            if not insert_data:
                raise ValueError("No valid data provided for deck creation")

            with self:
                columns = ", ".join(insert_data.keys())
                placeholders = ", ".join(["%s"] * len(insert_data))
                sql_query = f"""
                    INSERT INTO decks ({columns})
                    VALUES ({placeholders})
                    RETURNING *;
                """
                params = tuple(insert_data.values())
                self.cursor.execute(sql_query, params)
                self.conn.commit()
                return self.cursor.fetchone()

        except Exception as e:
            print(f"Error in DeckDao.create: {e}")
            raise

    def update(self, id, **kwargs):
        """
        Updates an existing deck by ID with the given attributes.

        Args:
            id (int): Deck ID to update.
            **kwargs: Columns to update with their new values.

        Returns:
            dict: Updated deck record, or None if deck does not exist.

        Raises:
            ValueError: If invalid keys are provided.
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
                        UPDATE decks
                        SET {set_clause}
                        WHERE deck_id = %s
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
        return None

    def delete(self, id):
        """
        Deletes a deck by its ID from decks, and removes all references
        in user_deck_link and deck_cards. Does not delete users or cards.

        Args:
            id (int): Deck ID to delete.

        Returns:
            dict: Deleted deck record from decks table.

        Raises:
            Exception: If deletion fails.
        """
        if self.exist(id):
            try:
                with self:
                    # Delete references in deck_cards first
                    sql_deck_cards = """
                    DELETE FROM deck_cards
                    WHERE deck_id = %s;
                    """
                    self.cursor.execute(sql_deck_cards, (id,))

                    # Delete references in user_deck_link
                    sql_user_link = """
                    DELETE FROM user_deck_link
                    WHERE deck_id = %s;
                    """
                    self.cursor.execute(sql_user_link, (id,))

                    # Finally, delete the deck itself
                    sql_deck = """
                    DELETE FROM decks
                    WHERE deck_id = %s
                    RETURNING *;
                    """
                    self.cursor.execute(sql_deck, (id,))
                    deleted_deck = self.cursor.fetchone()

                    # Commit all deletions
                    self.conn.commit()
                    return deleted_deck

            except Exception as e:
                print(f"Error deleting deck {id}: {e}")
                raise

    def get_all_deck_user_id(self, user_id: int) -> list:
        """
        Retrieves all deck IDs associated with a specific user.

        Args:
            user_id (int): User ID to fetch decks for.

        Returns:
            list[int]: List of deck IDs.
        """
        try:
            with self:
                sql_query = """
                SELECT D.deck_id
                FROM decks D
                JOIN user_deck_link UDLC
                ON D.deck_id = UDLC.deck_id
                WHERE UDLC.user_id = %s;
                """
                param = (user_id,)
                self.cursor.execute(sql_query, param)
                rows = self.cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

    def add_card_to_deck(self, deck_id: int, card_id: int):
        """
        Adds a card to a deck. If the card already exists in the deck,
        its quantity is increased by 1.

        Args:
            deck_id (int): Deck ID to add the card to.
            card_id (int): Card ID to add.

        Returns:
            list: Resulting rows (if any).

        Raises:
            ValueError: If the deck or card does not exist.
        """
        card = CardDao()
        if not card.exist(card_id):
            raise ValueError(f"Card {card_id} does not exist.")
        if not self.exist(deck_id):
            raise ValueError(f"Deck {deck_id} does not exist.")
        try:
            with self:
                sql_query = """
                INSERT INTO deck_cards(deck_id, card_id, quantity)
                VALUES (%s, %s, 1)
                ON CONFLICT (deck_id, card_id)
                DO UPDATE SET quantity = deck_cards.quantity + 1;
                """
                param = (deck_id, card_id)
                self.cursor.execute(sql_query, param)
                rows = self.cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

    def remove_card_from_deck(self, deck_id: int, card_id: int, all=False):
        """
        Removes a card from a deck. Can remove one quantity or all quantities.

        Args:
            deck_id (int): Deck ID to remove the card from.
            card_id (int): Card ID to remove.
            all (bool): If True, remove all quantities. Defaults to False.

        Returns:
            int or None: Remaining quantity after removal, or None if card was not found.

        Raises:
            ValueError: If the deck or card does not exist.
        """
        card = CardDao()
        if not card.exist(card_id):
            raise ValueError(f"Card {card_id} does not exist.")
        if not self.exist(deck_id):
            raise ValueError(f"Deck {deck_id} does not exist.")
        try:
            with self:
                if all:
                    sql_delete = """
                        DELETE FROM deck_cards
                        WHERE deck_id = %s AND card_id = %s
                        RETURNING *;
                    """
                    self.cursor.execute(sql_delete, (deck_id, card_id))
                    deleted_row = self.cursor.fetchone()
                    return 0 if deleted_row else None
                else:
                    sql_update = """
                        UPDATE deck_cards
                        SET quantity = quantity - 1
                        WHERE deck_id = %s AND card_id = %s AND quantity > 1
                        RETURNING quantity;
                    """
                    self.cursor.execute(sql_update, (deck_id, card_id))
                    row = self.cursor.fetchone()
                    if row is not None:
                        return row[0]
                    sql_delete = """
                        DELETE FROM deck_cards
                        WHERE deck_id = %s AND card_id = %s
                        RETURNING *;
                    """
                    self.cursor.execute(sql_delete, (deck_id, card_id))
                    deleted_row = self.cursor.fetchone()
                    return 0 if deleted_row else None
        except Exception as e:
            print(f"Error in remove_card_from_deck(): {e}")
            raise

    def create_user_deck(self, user_id: int, **kwargs):
        """
        Creates a new deck for a specific user and links it to the user.

        Args:
            user_id (int): ID of the user who will own the deck.
            **kwargs: Deck attributes to create (must be valid columns).

        Returns:
            dict: Dictionary containing the created deck and the user-deck link:
                {
                    "deck": {...},  # created deck record
                    "link": {...}   # user-deck link record
                }
                Returns None if deck creation fails.

        Raises:
            ValueError: If the user does not exist or invalid keys are provided.
            Exception: If the database operation fails.
        """
        player_dao = PlayerDao()
        if player_dao.exist(user_id):
            if not (set(kwargs.keys()).issubset(self.columns_valid)):
                raise ValueError(
                    f"Invalid keys : {set(kwargs.keys()) - self.columns_valid}"
                )
            try:
                new_deck = self.create(**kwargs)

                if not new_deck or "deck_id" not in new_deck:
                    raise ValueError("Deck creation failed — no deck_id returned.")

                deck_id = new_deck["deck_id"]
                with self:
                    sql_link = """
                    INSERT INTO user_deck_link (user_id, deck_id)
                    VALUES (%s, %s)
                    RETURNING *;
                    """
                    params = (user_id, deck_id)
                    self.cursor.execute(sql_link, params)
                    link_row = self.cursor.fetchone()
                    self.conn.commit()
                return {
                    "deck": new_deck,
                    "link": link_row
                }
            except Exception as e:
                print(f"Error in DeckDao.create_user_deck: {e}")
                raise
        else:
            return None

    def get_by_id_player(self, deck_id, user_id):
        """
        Checks if a specific user owns a specific deck.

        Args:
            deck_id (int): Deck ID to check.
            user_id (int): User ID to check ownership.

        Returns:
            bool: True if the user owns the deck, False if not.
            None: If the deck or user does not exist.

        Raises:
            Exception: If the database operation fails.
        """
        player_dao = PlayerDao()
        if self.exist(deck_id):
            if player_dao.exist(user_id):
                try:
                    with self:
                        sql_query = """
                        SELECT deck_id
                        FROM user_deck_link udl
                        WHERE udl.user_id = %s
                        AND udl.deck_id = %s;
                        """
                        params = (user_id, deck_id)
                        self.cursor.execute(sql_query, params)
                        rows = self.cursor.fetchone()
                        if rows is None:
                            return False
                        else:
                            return True
                except Exception as e:
                    print(f"Error in PlayerDao.player_get_deck: {e}")
                    raise
        else:
            return None

    def create_by_player(self, user_id, **kwargs):
        """
        Creates a new deck and links it to a user. Returns the new deck and user ID.

        Args:
            user_id (int): User ID to link the deck to.
            **kwargs: Deck attributes to create (must be valid columns).

        Returns:
            tuple: (user_id, deck_id) of the newly created deck.

        Raises:
            ValueError: If invalid keys are provided or deck creation fails.
            Exception: If the database operation fails.
        """
        player_dao = PlayerDao()
        if player_dao.exist(user_id):
            try:
                invalid_keys = set(kwargs.keys()) - self.columns_valid
                if invalid_keys:
                    raise ValueError(f"Invalid keys: {invalid_keys}")

                insert_data = {k: v for k, v in kwargs.items() if k != "deck_id"}

                if not insert_data:
                    raise ValueError("No valid data provided for deck creation")
                self.create(**kwargs)
                with self:
                    self.cursor.execute("""
                        SELECT deck_id
                        FROM decks
                        ORDER BY created_at DESC
                        LIMIT 1;
                    """)
                    row = self.cursor.fetchone()
                    if not row:
                        raise ValueError("No deck found after creation.")
                    new_deck_id = row["deck_id"]
                    sql_query = """
                        INSERT INTO user_deck_link (user_id, deck_id)
                        VALUES (%s, %s);
                    """
                    params = (user_id, new_deck_id)
                    self.cursor.execute(sql_query, params)
                    self.conn.commit()
                    return (user_id, new_deck_id)

            except Exception as e:
                print(f"Error in DeckDao.create_by_player: {e}")
                raise

    def update_by_player(self, user_id, deck_id):
        player_dao = PlayerDao()
        if player_dao.exist(user_id):
            if self.exist(deck_id):
                return self.update(deck_id)

    def delete_by_player(self, user_id, deck_id):
        """
        Deletes a deck owned by a specific user.

        Args:
            user_id (int): User ID who owns the deck.
            deck_id (int): Deck ID to delete.

        Returns:
            dict: The deleted deck record.

        Raises:
            ValueError: If the user or deck does not exist.
        """
        player_dao = PlayerDao()
        if player_dao.exist(user_id):
            self.delete(deck_id)
