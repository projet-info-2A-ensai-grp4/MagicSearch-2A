import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from dao.userDao import UserDao
from utils.dbConnection import dbConnection


class PlayerDao(UserDao):
    def searchCards(self, query_embedding, filters=None, limit=5):
        """
        Search for Magic cards using vector similarity search.

        Parameters
        ----------
        query_embedding : list or array
            The embedding vector to search for similar cards.
        filters : dict, optional
            Additional filters to apply (e.g., {'color': 'blue', 'type': 'creature'}).
            Default is None.
        limit : int, optional
            Maximum number of results to return. Default is 5.

        Returns
        -------
        list
            List of dictionaries containing card information and similarity distance.

        Raises
        ------
        ValueError
            If limit is not positive.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")

        conn = None
        try:
            with dbConnection() as conn:
                # Register pgvector extension
                register_vector(conn)

                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build base query
                    query = """
                        SELECT 
                            id,
                            card_name,
                            card_text,
                            card_type,
                            color,
                            mana_cost,
                            embedding <-> %s::vector as distance
                        FROM cards
                    """

                    params = [query_embedding]

                    # Add filters if provided
                    if filters:
                        conditions = []
                        for key, value in filters.items():
                            conditions.append(f"{key} = %s")
                            params.append(value)
                        if conditions:
                            query += " WHERE " + " AND ".join(conditions)

                    query += """
                        ORDER BY distance
                        LIMIT %s
                    """
                    params.append(limit)

                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    return results

        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e
