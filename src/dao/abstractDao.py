from abc import ABC, abstractmethod
import psycopg2


class AbstractDao(ABC):
    def __init__(self):
        self.conn_params = {
            # not a problem bc the postgres is only availabe through local network
            "host": "postgresql-885217.user-victorjean",
            "port": 5432,
            "database": "defaultdb",
            "user": "user-victorjean",
            "password": "pr9yh1516s57jjnmw7ll",
        }
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Enable context manager support."""
        self.conn = psycopg2.connect(**self.conn_params)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are closed."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    @abstractmethod
    def exist(self, id):
        pass

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_by_id(self, id):
        pass

    @abstractmethod
    def update(self, id, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, entity_id):
        pass
