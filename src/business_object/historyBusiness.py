from dao.historyDao import HistoryDao
from dao.userDao import UserDao


class HistoryBusiness():
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
        if len(hist) >= 5:
            min_id = min(row['history_id'] for row in hist)
            self.history.delete(min_id)
        new_line = self.history.create(user_id, prompt)
        return new_line
