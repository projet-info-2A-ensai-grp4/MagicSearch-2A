from dao.cardDao import CardDao
import requests
from dotenv import load_dotenv
import os


class CardBusiness:
    def __init__(self, dao: CardDao, card_id: int):
        self.dao = dao
        with dao:
            card_data = dao.get_card_by_id(card_id)
            if card_data is None:
                raise ValueError(f"Card with ID {card_id} does not exist.")
            # Map card_data to instance attributes
            for key, value in card_data.items():
                setattr(self, key, value)

    def __repr__(self):
        attributes = ", ".join(
            f"{key}={getattr(self, key)}" for key in vars(self)
        )
        return f"CardBusiness({attributes})"

    def generate_text_to_embed(self):
        """Generate and update the text_to_embed attribute of a card."""
        if not self.id:
            raise ValueError(
                "Impossible to generate text_to_embed without a card ID."
            )

        fields = [
            self.name,
            self.type,
            self.text,
            ", ".join(self.colors) if self.colors else None,
        ]
        text_to_embed = " | ".join(filter(None, fields))

        with self.dao:
            self.dao.edit_text_to_embed(text_to_embed, self.id)

        self.text_to_embed = text_to_embed
        return text_to_embed

    def vectorize(
        self, text: str, endpoint_url: str, api_key: str = None
    ) -> list:
        """
        Vectorize the given text using the Ollama API.

        Args:
            text (str): The text to vectorize.
            endpoint_url (str): The URL of the Ollama embedding endpoint.
            api_key (str, optional): API key for authentication (if required).

        Returns:
            list: The vectorized embedding of the text.

        Raises:
            ValueError: If the request fails or the response is invalid.
        """
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Adapt the payload to match the curl request format
        payload = {
            "model": "bge-m3:latest",
            "input": [text],  # The input is expected as a list of strings
        }

        try:
            response = requests.post(
                endpoint_url, json=payload, headers=headers
            )
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the response JSON
            result = response.json()

            # Check if the response contains the embeddings
            if "embeddings" in result:
                self.embedding = result["embeddings"][0]
                with self.dao:
                    self.dao.edit_vector(self.embedding, self.id)
                return self.embedding
            else:
                raise ValueError(
                    "Invalid response format: 'embedding' field not found."
                )

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to vectorize text: {e}")


if __name__ == "__main__":
    with CardDao() as dao:
        try:
            business = CardBusiness(
                dao, 420
            )  # Replace 420 with a valid card_id
            print(business)
            print(f"Card name: {business.name}")
            print(f"Card text to embed: {business.text_to_embed}")

            # Update the endpoint URL to match the Ollama API
            endpoint_url = "https://llm.lab.sspcloud.fr/ollama/api/embed"

            # loading the dotenv
            load_dotenv()
            api_key = os.getenv("LLM_API_KEY")

            embedding = business.vectorize(
                business.text_to_embed, endpoint_url, api_key
            )
            print(f"Vectorized embedding: {embedding}")
            print(type(embedding))
        except ValueError as e:
            print(f"Error: {e}")
