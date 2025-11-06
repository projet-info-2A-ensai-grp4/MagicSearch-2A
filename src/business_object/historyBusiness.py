from dao.historyDao import HistoryDao
from dao.userDao import UserDao


class History():
    def __init__(self, history_dao: HistoryDao, user_dao: UserDao):
        self.history = history_dao
        self.user = user_dao
    
    def add(self, user_id, prompt):
        """
        Add a line in the history.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        hist = self.history.get_by_id(user_id)
        print(hist)


History(HistoryDao(), UserDao()).add(6, "Mon prompt")