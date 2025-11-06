import os
import re
import numpy as np
from dotenv import load_dotenv
from dao.cardDao import CardDao
from services.embeddingService import EmbeddingService


class CardBusiness:
    # Mapping dictionaries for normalization
    MANA_SYMBOLS = {
        "{W}": " white",
        "{U}": " blue",
        "{B}": " black",
        "{R}": " red",
        "{G}": " green",
        "{C}": " colorless",
        "{T}": " tap",
        "{Q}": " untap",
        "{E}": " energy",
        "{S}": " snow",
        "{X}": " X",
        "{Y}": " Y",
        "{Z}": " Z",
        # Hybrid mana
        "{W/U}": " white or blue",
        "{W/B}": " white or black",
        "{U/B}": " blue or black",
        "{U/R}": " blue or red",
        "{B/R}": " black or red",
        "{B/G}": " black or green",
        "{R/G}": " red or green",
        "{R/W}": " red or white",
        "{G/W}": " green or white",
        "{G/U}": " green or blue",
        # Phyrexian mana
        "{W/P}": " white phyrexian",
        "{U/P}": " blue phyrexian",
        "{B/P}": " black phyrexian",
        "{R/P}": " red phyrexian",
        "{G/P}": " green phyrexian",
        # Two-brid mana (hybrid with 2)
        "{2/W}": " two or white",
        "{2/U}": " two or blue",
        "{2/B}": " two or black",
        "{2/R}": " two or red",
        "{2/G}": " two or green",
    }

    NUMBER_WORDS = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "10": "ten",
        "11": "eleven",
        "12": "twelve",
        "13": "thirteen",
        "14": "fourteen",
        "15": "fifteen",
        "16": "sixteen",
        "20": "twenty",
    }

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

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize Magic: The Gathering card text by converting symbols to readable text.

        Parameters
        ----------
        text : str
            The text containing MTG symbols to normalize.

        Returns
        -------
        str
            The normalized text with symbols converted to words.
        """
        if not text:
            return text

        normalized = text

        # Replace generic mana costs like {2}, {15}, etc. FIRST
        def replace_number(match):
            num = match.group(1)
            return " " + CardBusiness.NUMBER_WORDS.get(num, num) + " "

        normalized = re.sub(r"\{(\d+)\}", replace_number, normalized)

        # Then replace mana symbols (order matters - do complex symbols first)
        for symbol, word in sorted(
            CardBusiness.MANA_SYMBOLS.items(), key=lambda x: len(x[0]), reverse=True
        ):
            normalized = normalized.replace(symbol, word + " ")

        # Clean up multiple spaces
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def generate_text_to_embed2(self):
        """Generate and update the text_to_embed attribute of a card using a template."""
        if not self.id:
            raise ValueError("Impossible to generate text_to_embed without a card ID.")

        # Build the description using the template
        parts = [f"{self.name} is a {self.type}" if self.type else self.name]

        # Add mana cost (normalized)
        if self.mana_cost:
            normalized_mana = self.normalize_text(self.mana_cost)
            parts.append(f"with mana cost {normalized_mana}")

        # Add power/toughness or other stats
        stats = []
        if self.power and self.toughness:
            stats.append(f"power/toughness {self.power}/{self.toughness}")
        if self.loyalty:
            stats.append(f"loyalty {self.loyalty}")
        if self.defense:
            stats.append(f"defense {self.defense}")
        if stats:
            parts.append(f"and {', '.join(stats)}")

        text_description = " ".join(parts) + "."

        # Add abilities/rules text (normalized)
        if self.text:
            normalized_text = self.normalize_text(self.text)
            text_description += f" It has the following abilities: {normalized_text}."

        # Add keywords
        if self.keywords:
            text_description += f" Keywords include: {self.keywords}."

        self.text_to_embed = text_description

        with self.dao:
            self.dao.edit_text_to_embed(self.text_to_embed, self.id)

        return self.text_to_embed

    def vectorize(self, text: str = None, normalize: bool = True) -> list:
        """
        Vectorize the given text (or text_to_embed if text is None).

        Parameters
        ----------
        text : str, optional
            The text to vectorize. If None, uses self.text_to_embed.
        normalize : bool, optional
            Whether to normalize the embedding vector to unit length. Default is True.

        Returns
        -------
        list
            The vectorized embedding of the text.
        """
        text_to_vectorize = text or self.text_to_embed
        if not text_to_vectorize:
            raise ValueError("No text available to vectorize.")

        self.embedding = self.embedding_service.vectorize(text_to_vectorize)

        # Normalize the embedding if requested
        if normalize and self.embedding:
            embedding_array = np.array(self.embedding)
            norm = np.linalg.norm(embedding_array)
            if norm > 0:
                self.embedding = (embedding_array / norm).tolist()

        with self.dao:
            self.dao.edit_vector(self.embedding, self.id)

        return self.embedding


if __name__ == "__main__":
    with CardDao() as dao:
        # print(dao.get_by_id(420))

        try:
            business = CardBusiness(dao, 3)
            business.generate_text_to_embed2()
            print(business.text_to_embed)
            embedding = business.vectorize()
            print(business.embedding[:10])

        except ValueError as e:
            print(f"Error: {e}")
