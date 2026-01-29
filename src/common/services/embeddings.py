from langchain_openai import OpenAIEmbeddings
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()

    def embed_query(self, text: str) -> List[float]:
        """
        Generates an embedding for a single piece of text.
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error generating embeddings for documents: {e}")
            raise e

# Global instance for easy access
embeddings_service = EmbeddingsService()
