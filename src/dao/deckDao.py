from dao.abstractDao import AbstractDao
from dao.cardDao import CardDao
from dao.playerDao import PlayerDao


class DeckDao(AbstractDao):

    columns_valid = {"deck_id", "name", "type"}

    def shape(self):
        """
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
        try:
            invalid_keys = set(kwargs.keys()) - self.columns_valid
            if invalid_keys:
                raise ValueError(f"Invalid keys: {invalid_keys}")

            # Ne pas insérer deck_id s’il est auto-généré
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
        if self.exist(id):
            try:
                with self:
                    sql_query = """
                    DELETE FROM decks
                    WHERE deck_id = %s
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

    # Methode spe (get deck by user_i)
    # Add card to deck by deck_id  & card_id
    # leave card to deck by deck_id & card_id

    def get_all_deck_user_id(self, user_id: int) -> list:
        """
        return list of deck_id
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
                param = (deck_id, card_id,)
                self.cursor.execute(sql_query, param)
                rows = self.cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit()

    def remove_card_from_deck(self, deck_id: int, card_id: int, all=False):
        """
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
