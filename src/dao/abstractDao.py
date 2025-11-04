from abc import ABC, abstractmethod
from dbconnection import dbConnection


class AbstractDao(ABC):
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Utilisation du context manager de dbConnection"""
        self.db = dbConnection()
        self.conn = self.db.__enter__()  # ouvre la connexion via dbConnection
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme proprement le curseur et la connexion"""
        if self.cursor:
            self.cursor.close()
        # on délègue la fermeture à dbConnection
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
