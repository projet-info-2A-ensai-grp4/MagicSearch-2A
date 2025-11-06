import psycopg2
from .abstractDao import AbstractDao


class HistoryDao(AbstractDao):
    # CREATE
    def create(self, user_id, prompt):
        """
        Add a line in the history of a user, when a research is done.

        Parameters
        ----------
        user_id : int
            The user id.
        prompt : str
            The research.

        Returns
        -------
        row : dict
            Dictionary containing the user_id and its new research:
            {'user_id': int, 'prompt': str}.

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
                    "INSERT INTO histories (user_id,   "
                    "                       prompt)    "
                    "VALUES (%s, %s)                   "
                    "RETURNING user_id, prompt        ",
                    (user_id, prompt),
                )
                row = self.cursor.fetchone()
                self.conn.commit()
                return row
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # READ
    def exist(self, id):
        """
        The exist method is not useful for the HistoriesDao class.
        """
        pass

    def get_by_id(self, id):
        """
        Get the history of a user.

        Parameters
        ----------
        id : int
            The user_id.
        
        Returns
        -------
        hist : dict
            Dictionary containing the user's history:
            {'history_id': int, 'user_id': int, 'prompt': str}.
        """
        try:
            with self:
                self.cursor.execute(
                    "SELECT history_id,       "
                    "       user_id,          "
                    "       prompt            "
                    "FROM histories           "
                    "WHERE user_id = %s       ",
                    (id,),
                )
                hist = self.cursor.fetchall()
                return hist
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    # UPDATE
    def update(self, id):
        """
        The update method is not useful for the HistoriesDao class.
        """
        pass

    # DELETE
    def delete(self, id):
        """
        Delete a line in the history.

        Parameters
        ----------
        id : list[int]
            List containing the history_id.

        Returns
        -------
        del_his : dict
            Dictionary containing the deleted line in the history:
            {'user_id': int, 'prompt': str}

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
                    "DELETE FROM histories            "
                    "WHERE history_id = %s            "
                    "RETURNING user_id, prompt        ",
                    (id,),
                )
                del_his = self.cursor.fetchone()
                self.conn.commit()
                return del_his
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
