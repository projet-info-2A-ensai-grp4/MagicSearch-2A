from abc import ABC, abstractmethod
import sys
from utils.dbConnection import dbConnection
from psycopg2.extras import RealDictCursor


class AbstractDao(ABC):
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.db = dbConnection()
        try:
            self.conn = self.db.__enter__()
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception:
            self.db.__exit__(*sys.exc_info())
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        self.db.__exit__(exc_type, exc_val, exc_tb)

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
    def delete(self, id):
        pass
