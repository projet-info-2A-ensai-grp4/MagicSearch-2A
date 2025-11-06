from dao.userDao import UserDao


class UserBusiness:
    def __init__(self, username, email):
        self.username = username
        self.email = email
