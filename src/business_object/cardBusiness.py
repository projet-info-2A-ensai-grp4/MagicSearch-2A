import os
from dotenv import load_dotenv
from dao.cardDao import CardDao
from services.embeddingService import EmbeddingService

class CardBusiness:
    def __init__(
        self, dao: CardDao, card_id: int, embedding_service: EmbeddingService = None
    ):
        self.dao = dao
        self.embedding_service = embedding_service or EmbeddingService()
        with dao:
            card_data = dao.get_by_id(card_id)
            if card_data is None:
                raise ValueError(f"Card with ID {card_id} does not exist.")
            # Map card_data to instance attributes
            for key, value in card_data.items():
                setattr(self, key, value)

    def __repr__(self):
        attributes = ", ".join(f"{key}={getattr(self, key)}" for key in vars(self))
        return f"CardBusiness({attributes})"

    def generate_text_to_embed2(self):
        """Generate and update the text_to_embed attribute of a card."""
        if not self.id:
            raise ValueError("Impossible to generate text_to_embed without a card ID.")

        text_description = f"This is the description of a Magic The Gathering card, be aware that the description of the card may have some missing values, it is not a problem, it just means the card does not contain that kind of information (for example a spell usually does not have power and life). You know and master the rules of the Magic: The Gathering card game. If you need some explanation of the card, know that the cost is displayed like {{2}}{{R}}{{G}}{{B}}{{W}}{{U}}, which means 2 mana + 1 red + 1 green + 1 blue + 1 white + 1 uncolor, you understand the rest. for your notice {{T}} means to tap the card. Here are the most important caracteristics of a card: its name is {self.name}, its type is {self.type} and its description text is ``{self.text}''. Finally, the card cost is {self.mana_cost}. Logically the total mana value is {self.mana_value}. The power of the card is {self.power} and its toughness is {self.toughness}, its color identity is {self.color_identity}. The card also may have keywords (refer to the mtg rules): {self.keywords}."

        self.text_to_embed = text_description

        with self.dao:
            self.dao.edit_text_to_embed(self.text_to_embed, self.id)

        return self.text_to_embed

    def vectorize(self, text: str = None) -> list:
        """
        Vectorize the given text (or text_to_embed if text is None).

        Parameters
        ----------
        text : str, optional
            The text to vectorize. If None, uses self.text_to_embed.

        Returns
        -------
        list
            The vectorized embedding of the text.
        """
        text_to_vectorize = text or self.text_to_embed
        if not text_to_vectorize:
            raise ValueError("No text available to vectorize.")

        self.embedding = self.embedding_service.vectorize(text_to_vectorize)

        with self.dao:
            self.dao.edit_vector(self.embedding, self.id)

        return self.embedding


if __name__ == "__main__":
    with CardDao() as dao:
        print(dao.get_by_id(420))

        try:
            business = CardBusiness(dao, 420)
            business.generate_text_to_embed2()
            embedding = business.vectorize()

        except ValueError as e:
            print(f"Error: {e}")
