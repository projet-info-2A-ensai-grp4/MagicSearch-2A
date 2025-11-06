from dao.favoritesDao import FavoritesDao
from dao.userDao import UserDao
from dao.cardDao import CardDao


class FavoriteBusiness:
    def __init__(self, favorites_dao, user_dao, card_dao):
        self.favorites = favorites_dao
        self.user = user_dao
        self.card = card_dao
    
    def add_favorite(self, user_id, card_id):
        """
        Add a card to user's favorites.

        Parameters
        ----------
        user_id : int
            The user id.
        card_id : int
            The card id to add as favorite.
        
        Returns
        -------
        dict :
            Dictionnary containing the favorite information :
            {'user_id': int, 'card_id': int, 'added_at': datetime}.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        if not self.card.exist(card_id):
            raise ValueError("This card_id does not exist")
        if self.favorites.exist([user_id, card_id]):
            return {"user_id": user_id, "card_id": card_id}
        row = self.favorites.create(user_id, card_id)
        return row
    
    def remove_favorite(self, user_id, card_id):
        """
        Remove a card from a user's favorites.

        Parameters
        ----------
        user_id : int
            The user id.
        card_id : int
            The card id to remove from the favorite.
        
        Returns
        -------
        dict :
            Dictionnary containing the favorite information :
            {'user_id': int, 'card_id': int}.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        if not self.card.exist(card_id):
            raise ValueError("This card_id does not exist")
        if not self.favorites.exist([user_id, card_id]):
            raise ValueError("This favorite_id does not exist")
        row = self.favorites.delete([user_id, card_id])
        return row