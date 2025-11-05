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

        # Create a rich, natural language description optimized for embedding models
        parts = []

        # Core identity - name is the anchor
        parts.append(f"Card: {self.name}")

        # Type line (critical for searching by card type)
        if self.type:
            parts.append(f"Type: {self.type}")

        # Supertypes, types, and subtypes for granular search
        type_parts = []
        if self.supertypes:
            type_parts.append(f"Supertypes: {self.supertypes}")
        if self.types:
            type_parts.append(f"Types: {self.types}")
        if self.subtypes:
            type_parts.append(f"Subtypes: {self.subtypes}")
        if type_parts:
            parts.append(". ".join(type_parts))

        # Mana and cost (important for deck building searches)
        if self.mana_cost:
            parts.append(f"Mana cost: {self.mana_cost}")
        if self.mana_value:
            parts.append(f"Total mana value: {self.mana_value}")

        # Color information (essential for color identity searches)
        if self.colors:
            parts.append(f"Colors: {self.colors}")
        if self.color_identity:
            parts.append(f"Color identity: {self.color_identity}")
        if self.color_indicator:
            parts.append(f"Color indicator: {self.color_indicator}")

        # Card text - THE MOST IMPORTANT for semantic search
        if self.text:
            parts.append(f"Rules text: {self.text}")

        # Combat and game stats
        stats = []
        if self.power and self.toughness:
            stats.append(f"Power/Toughness: {self.power}/{self.toughness}")
        if self.loyalty:
            stats.append(f"Loyalty: {self.loyalty}")
        if self.defense:
            stats.append(f"Defense: {self.defense}")
        if stats:
            parts.append(". ".join(stats))

        # Keywords (crucial for mechanic searches)
        # Note: Embedding models may not know MTG keyword meanings without context.
        # Consider fetching keyword rules from Scryfall API or MTG Comprehensive Rules.
        # For now, we list them to help the model learn associations through usage patterns.
        if self.keywords:
            parts.append(f"Keywords: {self.keywords}")
            # TODO: Enhance with keyword descriptions from a keyword glossary
            # Example: "Flying (This creature can't be blocked except by creatures with flying or reach)"

        # Format and legality indicators
        if self.subsets:
            parts.append(f"Subsets: {self.subsets}")

        # Special properties
        special = []
        if self.is_reserved:
            special.append("Reserved List card")
        if self.is_funny:
            special.append("Un-set or funny card")
        if self.has_alternative_deck_limit:
            special.append("Alternative deck limit")
        if special:
            parts.append(". ".join(special))

        # Layout info for split/flip/transform cards
        if self.layout and self.layout not in ["normal", "token"]:
            parts.append(f"Layout: {self.layout}")
        if self.face_name and self.face_name != self.name:
            parts.append(f"Other face: {self.face_name}")

        # Join into natural, flowing text
        text_description = ". ".join(filter(None, parts))
        if not text_description.endswith("."):
            text_description += "."

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
        # print(dao.get_by_id(420))

        try:
            business = CardBusiness(dao, 422)
            business.generate_text_to_embed2()
            print(business.text_to_embed)
            embedding = business.vectorize()

        except ValueError as e:
            print(f"Error: {e}")
