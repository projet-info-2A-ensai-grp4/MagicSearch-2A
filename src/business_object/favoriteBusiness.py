from dao.favoritesDao import FavoritesDao


class FavoriteBusiness:
    def __init__(self, username, email):
        self.username = username
        self.email = email