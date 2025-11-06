import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from dao.userDao import UserDao
from utils.dbConnection import dbConnection
from services.embeddingService import EmbeddingService
import numpy


class PlayerDao(UserDao):
    def __init__(self, embedding_service: EmbeddingService = None):
        """
        Initialize PlayerDao with an optional embedding service.

        Parameters
        ----------
        embedding_service : EmbeddingService, optional
            Service for generating embeddings. If None, creates a new instance.
        """
        super().__init__()
        self.embedding_service = embedding_service or EmbeddingService()

    def natural_language_search(self, query, filters=None, limit=5):
        """
        Search for Magic cards using vector similarity search.

        Parameters
        ----------
        query : str or list
            Either a text query (str) to be embedded, or an embedding vector (list).
        filters : dict, optional
            Additional filters to apply (e.g., {'colors': ['U', 'B'], 'mana_value__gte': 3}).
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
            If limit is not positive or query is invalid.
        ConnectionError
            If the database connection fails.
        RuntimeError
            If an unexpected database error occurs.
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")

        # Handle query: embed text on-the-fly if it's a string
        if isinstance(query, str):
            query_embedding = self.embedding_service.vectorize(query)
        elif isinstance(query, (list, tuple, numpy.ndarray)):
            query_embedding = query
        else:
            raise ValueError("Query must be either a string or an embedding vector")

        conn = None
        try:
            with dbConnection() as conn:
                register_vector(conn)

                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query_sql = """
                        SELECT
                            id,
                            name,
                            text,
                            type,
                            color_identity,
                            mana_cost,
                            mana_value,
                            image_url,
                            embedding <-> %s::vector as distance
                        FROM cards
                    """

                    params = [query_embedding]

                    # Build WHERE clause for filters
                    conditions = []
                    if filters:
                        for key, value in filters.items():
                            # Handle comparison operators (mana_value__gte, mana_value__lte)
                            if "__" in key:
                                field, operator = key.rsplit("__", 1)

                                if operator == "gte":
                                    conditions.append(f"{field} >= %s")
                                    params.append(value)
                                elif operator == "lte":
                                    conditions.append(f"{field} <= %s")
                                    params.append(value)
                                elif operator == "gt":
                                    conditions.append(f"{field} > %s")
                                    params.append(value)
                                elif operator == "lt":
                                    conditions.append(f"{field} < %s")
                                    params.append(value)
                            # Handle color array filter
                            elif key == "colors" and isinstance(value, list):
                                # Use && operator for array overlap
                                conditions.append("colors && %s")
                                params.append(value)
                            # Handle simple equality
                            else:
                                conditions.append(f"{key} = %s")
                                params.append(value)

                    if conditions:
                        query_sql += " WHERE " + " AND ".join(conditions)

                    query_sql += """
                        ORDER BY distance
                        LIMIT %s
                    """
                    params.append(limit)

                    cursor.execute(query_sql, params)
                    results = cursor.fetchall()
                    return results

        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e

    def get_card_embedding(self, card_id):
        """Get the embedding vector for a specific card."""
        conn = None
        try:
            with dbConnection() as conn:
                register_vector(conn)

                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT embedding FROM cards WHERE id = %s", (card_id,)
                    )
                    result = cursor.fetchone()
                    return result["embedding"] if result else None

        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected database error: {e}") from e


def player_get_deck(self, deck_id, user_id):
    """ """
    from deckDao import DeckDao

    if DeckDao.exist(deck_id):
        if self.exist(user_id):
            try:
                with self:
                    sql_query = """" SELECT deck_ FROM user_deck_link udl
                    WHERE udl.user_id = %s
                    AND udl.deck_id = %s;
                    """
                params = (
                    user_id,
                    deck_id,
                )
                rows = self.cursor.execute(sql_query, params)
                if rows is None:
                    return False
                else:
                    return True
            except Exception as e:
                print(f"Error in PlayerDao.player_get_deck: {e}")
                raise
    else:
        return None


if __name__ == "__main__":
    player_dao = PlayerDao()

    try:
        # Test with filters
        print("Test: Searching with filters...")
        results = player_dao.natural_language_search(
            "powerful creatures",
            filters={"colors": ["U", "B"], "mana_value__lte": 4},
            limit=5,
        )
        print(f"Found {len(results)} cards:")
        for card in results:
            print(
                f"  - {card['name']} (CMC: {card.get('mana_value', 'N/A')},"
                f" distance: {card['distance']:.4f})"
            )

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
