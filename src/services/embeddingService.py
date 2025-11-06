import requests
from dotenv import load_dotenv
import os
import numpy as np


class EmbeddingService:
    """Service for generating embeddings using the Ollama API."""

    def __init__(self, endpoint_url=None, api_key=None):
        """
        Initialize the embedding service.

        Parameters
        ----------
        endpoint_url : str, optional
            The URL of the Ollama embedding endpoint.
            If None, uses default from environment.
        api_key : str, optional
            API key for authentication. If None, loads from .env file.
        """
        load_dotenv()
        self.endpoint_url = endpoint_url or os.getenv(
            "EMBEDDING_ENDPOINT_URL", "https://llm.lab.sspcloud.fr/ollama/api/embed"
        )
        self.api_key = api_key or os.getenv("LLM_API_KEY")

    def vectorize(self, text: str, normalize: bool = True) -> list:
        """
        Vectorize the given text using the Ollama API.

        Parameters
        ----------
        text : str
            The text to vectorize.
        normalize : bool, optional
            Whether to normalize the embedding to unit length. Default is True.

        Returns
        -------
        list
            The vectorized embedding of the text.

        Raises
        ------
        ValueError
            If the request fails or the response is invalid.
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": "bge-m3:latest",
            "input": [text],
        }

        try:
            response = requests.post(self.endpoint_url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if "embeddings" in result:
                embedding = result["embeddings"][0]

                # Normalize the embedding if requested
                if normalize:
                    embedding_array = np.array(embedding)
                    norm = np.linalg.norm(embedding_array)
                    if norm > 0:
                        embedding = (embedding_array / norm).tolist()

                return embedding
            else:
                raise ValueError(
                    "Invalid response format: 'embedding' field not found."
                )

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to vectorize text: {e}")
