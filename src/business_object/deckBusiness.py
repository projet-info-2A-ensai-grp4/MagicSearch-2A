from dao.deckDao import DeckDao
from dao.userDao import UserDao
from dao.cardDao import CardDao
from datetime import datetime


class DeckBusiness:
    def __init__(self, deck_dao: DeckDao, user_dao: UserDao, card_dao: CardDao):
        self.deck = deck_dao
        self.user = user_dao
        self.card = card_dao

    def add_card_to_deck(self, user_id, card_id, deck_id):
        """
        Add a card to a user's deck.

        Parameters
        ----------
        user_id : int
            The user id.
        card_id : int
            The card id to add to the deck.
        deck_id : int
            The deck id to which the card will be added.

        Returns
        -------
        dict :
            Dictionary containing the deck information :
            {'user_id': int, 'deck_id': int, 'card_id': int, 'added_at': datetime}.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        if not self.card.exist(card_id):
            raise ValueError("This card_id does not exist")
        if not self.deck.exist(deck_id):
            raise ValueError("This deck_id does not exist")

        user_decks = self.deck.get_all_decks_from_user(user_id)
        deck_belongs_to_user = any(deck['deck_id'] == deck_id for deck in user_decks)
        if not deck_belongs_to_user:
            raise ValueError("This deck does not belong to the user")

        self.deck.add_card_to_deck(card_id, deck_id)

        return {
            'user_id': user_id,
            'deck_id': deck_id,
            'card_id': card_id,
            'added_at': datetime.now()
        }

    def remove_card_from_deck(self, user_id, card_id, deck_id):
        """
        Remove a card from a user's deck.

        Parameters
        ----------
        user_id : int
            The user id.
        card_id : int
            The card id to remove from the deck.
        deck_id : int
            The deck id from which the card will be removed.

        Returns
        -------
        dict :
            Dictionary containing the deck information :
            {'user_id': int, 'deck_id': int, 'card_id': int, 'removed_at': datetime}.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        if not self.card.exist(card_id):
            raise ValueError("This card_id does not exist")
        if not self.deck.exist(deck_id):
            raise ValueError("This deck_id does not exist")

        user_decks = self.deck.get_all_decks_from_user(user_id)
        deck_belongs_to_user = any(deck['deck_id'] == deck_id for deck in user_decks)
        if not deck_belongs_to_user:
            raise ValueError("This deck does not belong to the user")

        deleted_row = self.deck.remove_card_from_deck(card_id, deck_id)
        if not deleted_row:
            raise ValueError("Card not found in the deck")

        return {
            'user_id': user_id,
            'deck_id': deck_id,
            'card_id': card_id,
            'removed_at': datetime.now()
        }

    def create_new_deck(self, user_id, deck_name, format):
        """
        Create a new deck for a user.

        Parameters
        ----------
        user_id : int
            The user id.
        deck_name : str
            The name of the new deck.
        format : str
            The format of the deck (e.g., 'Standard', 'Modern').

        Returns
        -------
        dict :
            Dictionary containing the new deck information :
            {'deck_id': int, 'user_id': int, 'deck_name': str, 'format': str}.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")

        created_deck = self.deck.create(user_id, deck_name, format)

        return {
            'deck_id': created_deck['deck_id'],
            'user_id': user_id,
            'deck_name': created_deck['name'],
            'format': created_deck['type']
        }

    def delete_deck(self, user_id, deck_id):
        """
        Delete a user's deck.

        Parameters
        ----------
        user_id : int
            The user id.
        deck_id : int
            The deck id to be deleted.

        Returns
        -------
        dict :
            Dictionary confirming deletion :
            {'deck_id': int, 'user_id': int, 'deleted_at': datetime}.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        if not self.deck.exist(deck_id):
            raise ValueError("This deck_id does not exist")

        user_decks = self.deck.get_all_decks_from_user(user_id)
        deck_belongs_to_user = any(deck['deck_id'] == deck_id for deck in user_decks)
        if not deck_belongs_to_user:
            raise ValueError("This deck does not belong to the user")

        self.deck.delete(deck_id)

        return {
            'deck_id': deck_id,
            'user_id': user_id,
            'deleted_at': datetime.now()
        }

    def get_user_decks(self, user_id):
        """
        Get all decks belonging to a user.

        Parameters
        ----------
        user_id : int
            The user id.

        Returns
        -------
        list :
            List of dictionaries containing deck information.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")

        return self.deck.get_all_decks_from_user(user_id)

    def get_deck_details(self, user_id, deck_id):
        """
        Get detailed information about a deck including its cards.

        Parameters
        ----------
        user_id : int
            The user id.
        deck_id : int
            The deck id.

        Returns
        -------
        list :
            List of dictionaries containing deck and card information.
        """
        if not self.user.exist(user_id):
            raise ValueError("This user_id does not exist")
        if not self.deck.exist(deck_id):
            raise ValueError("This deck_id does not exist")

        user_decks = self.deck.get_all_decks_from_user(user_id)
        deck_belongs_to_user = any(deck['deck_id'] == deck_id for deck in user_decks)
        if not deck_belongs_to_user:
            raise ValueError("This deck does not belong to the user")

        return self.deck.get_by_id(deck_id)
