import os
import psycopg2
from dotenv import load_dotenv

# Load variables from env file
load_dotenv()


class dbConnection:
    """
    Managing connection to Postgresql database
    """

    def __init__(self):
        self.conn = None

    def __enter__(self):
        """Ouvre la connexion à la base de données"""
        try:
            self.conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ.get("DB_PORT", 5432),
                database=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                sslmode="require",
            )

            return self.conn  # retourne la connexion pour utilisation

        except Exception as e:
            print(f"Erreur de connexion à la base : {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
