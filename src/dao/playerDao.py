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
                            scryfall_oracle_id,
                            embedding <-> %s::vector as distance
                        FROM cards
                    """

                    params = [query_embedding]

                    if filters:
                        conditions = []
                        for key, value in filters.items():
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


if __name__ == "__main__":
    player_dao = PlayerDao()

    try:
        # Test 1: Search using card id 420's embedding
        print("Test 1: Getting embedding from card id 422...")
        test_embedding = player_dao.get_card_embedding(422)

        if test_embedding is not None:
            results = player_dao.natural_language_search(test_embedding, limit=5)
            print(f"Found {len(results)} similar cards:")
            for card in results:
                print(f"  - {card['name']} (distance: {card['distance']:.4f})")

        # Test 2: Search using text query (embedded on-the-fly)
        print("\nTest 2: Searching with text query...")
        results = player_dao.natural_language_search("creature that goes well with a blue-black deck synergy around losing pv to draw cards", limit=5)
        print(f"Found {len(results)} cards:")
        for card in results:
            print(f"  - {card['name']} (distance: {card['distance']:.4f})")

    except Exception as e:
        print(f"Error running Tests: {type(e).__name__}: {e}")
