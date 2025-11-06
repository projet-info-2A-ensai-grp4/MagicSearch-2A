import psycopg2
from .abstractDao import AbstractDao


class FavoritesDao(AbstractDao):
    # CREATE
    def create(self, user_id, card_id):
        """
        Add a favorite card.

        Parameters
        ----------
        user_id : int
            The user id.
        card_id : int
            The id of the card the user wants to add as favorite.

        Returns
        -------
        row : dict
            Dictionary containing the user_id and the new favorite card_id
            for this user.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "INSERT INTO favorites (user_id,   "
                    "                       card_id)   "
                    "VALUES (%s, %s)                   "
                    "RETURNING user_id, card_id        ",
                    (user_id, card_id),
                )
                row = self.cursor.fetchone()
                self.conn.commit()
                return row
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
        
    # READ
    def exist(self, id: list):
        """
        Check if a card is a favorite of the user.

        Parameters
        ----------
        id : list[int]
            List containing the user_id and the card_id: [user_id, card_id].

        Returns
        -------
        bool :
            True if the card is a favorite, False if not.

        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT id FROM favorites              "
                    "WHERE user_id = %s AND card_id = %s   "
                    "LIMIT 1                               ",
                    (id[0], id[1]),
                )
                return self.cursor.fetchone() is not None
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
    
    def get_by_id(self, id):
        """
        List of the user's favorite cards.

        Parameters
        ----------
        id :
            The user id.
        """
        with self:
            self.cursor.execute(
                "SELECT card_id, created_at    "
                "FROM favorites                "
                "WHERE user_id = %s            "
                "ORDER BY created_at DESC      ",
                (id,),
            )
            return self.cursor.fetchall()

    # UPDATE
    def update(self, id):
        """
        The update method is not useful for the FavoriteDao class.
        """
        pass

    # DELETE
    def delete(self, id: list):
        """
        Delete a favorite card.

        Parameters
        ----------
        id : list[int]
            List containing the user_id and the card_id: [user_id, card_id].
        
        Returns
        -------
        del_fav : dict
            Dictionary containing the deleted favorite card information, such as 'user_id'
            and 'card_id'.
        
        Raises:
        -------
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        try:
            with self:
                self.cursor.execute(
                    "DELETE FROM favorites                 "
                    "WHERE user_id = %s AND card_id = %s   "
                    "RETURNING user_id, card_id            ",
                    (id[0], id[1]),
                )
                del_fav = self.cursor.fetchone()
                self.conn.commit()
                return del_fav
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e