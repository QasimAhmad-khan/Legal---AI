from abc import ABC, abstractmethod
import openai
from typing import List

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str):
        self.client = openai.Client(api_key=api_key)

    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

class SentenceTransformersEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        # Requires sentence-transformers package
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

class MockEmbeddingProvider(EmbeddingProvider):
    def get_embedding(self, text: str) -> List[float]:
        return [0.0] * 1536

def get_embedding_provider(provider_name: str, api_key: str = None) -> EmbeddingProvider:
    provider_name = provider_name.lower()
    if provider_name == "openai":
        return OpenAIEmbeddingProvider(api_key)
    elif provider_name == "sentence-transformers":
        return SentenceTransformersEmbeddingProvider()
    elif provider_name == "mock":
        return MockEmbeddingProvider()
    raise ValueError(f"Unknown embedding provider: {provider_name}")
